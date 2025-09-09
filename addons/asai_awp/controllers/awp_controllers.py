from odoo import http, fields
from odoo.http import request
import base64
import os

class TasksListController(http.Controller):
    def bus_broadcast(self, channel: str, message: dict):
        '''
        Метод для рассылки обновлений какой-либо задачи всем пользователям.
        В проде лучше рассылать только тем, кому надо
        '''
        bus = request.env['bus.bus']

        for user in request.env['res.users'].search([]):
            bus._sendone(user.partner_id, channel, message)


    @http.route('/awp/task-take', type='json', auth='user', methods=['POST'])
    def task_take(self, task_id):
        '''
        Контроллер взятия задачи в работу
        '''
        # Ищем запись в БД по ИД задачи
        record = request.env['awp.tasks'].search([('task_id', '=', task_id)])
        if not record:
            return {'error': 'Task not found'}
        
        # обновляем статус, ставим серверное время взятия в работу
        # и добавляем текущего пользователя в "список" тех, у кого эта задача уже в работе
        record.write({
            'order_status': 'in_progress',
            'taken_on': fields.Datetime.now(),
            'taken_by_ids': [(4, request.env.user.id)]
        })
        # для демонстрации, в проде можно не искать заново
        record = request.env['awp.tasks'].search([('task_id', '=', task_id)])

        # костыль, чтобы достать из модели ключи и лэйблы для статуса заказа/задачи
        selection_dict = dict(request.env['awp.tasks'].fields_get(['order_status'])['order_status']['selection'])

        # броадкастим всем пользователям обновление
        self.bus_broadcast(
            'task_update',
            {
                'task_id': record.task_id,
                'fields': {
                    'order_status_key': record.order_status,
                    'order_status_label': selection_dict.get(record.order_status),
                    'taken_on': record.taken_on,
                    'taken_by_logins': record.taken_by_ids.mapped('login')
                }
            }
        )

        # броадкаста достаточно, это осталось с уровня medium 
        # -- ответа success True будет достаточно
        return {
            'success': True,
            'task_id': record.task_id,
            'order_number': record.order_number,
            'new_status_key': record.order_status,
            'new_status_label': selection_dict.get(record.order_status),
            'taken_on': record.taken_on,
            'taken_by_logins': record.taken_by_ids.mapped('login'),
            'current_user_login': request.env.user.login
        }
    

    @http.route('/awp/task-done', type='json', auth='user', methods=['POST'])
    def task_done(self, task_id):
        '''
        Контроллер готовности задачи
        '''
        # аналогично
        record = request.env['awp.tasks'].search([('task_id', '=', task_id)])
        if not record:
            return {'error': 'Task not found'}
        
        # аналогично, но записываем время готовности
        record.write({
            'order_status': 'done',
            'done_on': fields.Datetime.now()
        })
        record = request.env['awp.tasks'].search([('task_id', '=', task_id)])

        # аналогично, костыль опять
        selection_dict = dict(request.env['awp.tasks'].fields_get(['order_status'])['order_status']['selection'])

        # аналогично
        self.bus_broadcast(
            'task_update',
            {
                'task_id': record.task_id,
                'fields': {
                    'order_status_key': record.order_status,
                    'order_status_label': selection_dict.get(record.order_status),
                    'done_on': record.done_on
                }
            }
        )

        # аналогично, уже не особо нужно
        return {
            'success': True,
            'task_id': record.task_id,
            'order_number': record.order_number,
            'new_status_key': record.order_status,
            'new_status_label': selection_dict.get(record.order_status),
            'done_on': record.done_on
        }
    

    @http.route('/awp/task-defect', type='json', auth='user', methods=['POST'])
    def task_defect(self, task_id, defect_reason):
        '''
        Контроллер брака
        '''
        # аналогично
        record = request.env['awp.tasks'].search([('task_id', '=', task_id)])
        if not record:
            return {'error': 'Task not found'}
        
        # аналогично, до дописываем причину брака
        record.write({
            'order_status': 'defect',
            'defect_reason': defect_reason
        })
        record = request.env['awp.tasks'].search([('task_id', '=', task_id)])

        # аналогично, костыль
        selection_dict = dict(request.env['awp.tasks'].fields_get(['order_status'])['order_status']['selection'])

        # аналогично
        self.bus_broadcast(
            'task_update',
            {
                'task_id': record.task_id,
                'fields': {
                    'order_status_key': record.order_status,
                    'order_status_label': selection_dict.get(record.order_status)
                }
            }
        )

        return {
            'success': True,
            'task_id': record.task_id,
            'order_number': record.order_number,
            'new_status_key': record.order_status,
            'new_status_label': selection_dict.get(record.order_status),
            'defect_reason': record.defect_reason
        }
    

    @http.route('/awp/task-hide', type='json', auth='user', methods=['POST'])
    def task_hide(self, task_id):
        '''
        Контроллер скрытия задачи
        (в БД и у клиента (при запросе списка задач) есть, но не отображается в UI)
        '''
        record = request.env['awp.tasks'].search([('task_id', '=', task_id)])
        if not record:
            return {'error': 'Task not found'}
        
        record.write({
            'hidden': True
        })
        record = request.env['awp.tasks'].search([('task_id', '=', task_id)])

        # упс, забыл дописать броадкаст и не показал в записи
        return {
            'success': True,
            'task_id': record.task_id,
            'order_number': record.order_number,
            'new_hidden': record.hidden
        }
    

    @http.route('/awp/tasks-json', type='json', auth='user')
    def tasks_json(self):
        '''
        Контроллер запроса списка задач
        '''
        # ищем все задачи,
        # а правила доступа, прописанные в security.xml и группы в demo_users.xml,
        # ограничивают выборку только для текущего пользователя
        tasks = request.env['awp.tasks'].search([])

        # опять костыль
        selection_dict = dict(request.env['awp.tasks'].fields_get(['order_status'])['order_status']['selection'])

        # сомнительно, но окэй
        default_preview_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'img', 'no_preview.png'
        )
        with open(default_preview_path, 'rb') as f:
            default_preview_b64 = base64.b64encode(f.read()).decode()
        
        tasks_list = list()

        for t in tasks:
            # ищем документ, который можно исопльзовать в качетве превью задачи
            preview_doc = next((d for d in t.documents if d.preview), None)

            # если превью-док нашёлся и у него не пустое поле file, т.е. есть запись в БД
            if preview_doc and preview_doc.file:
                # исопльзуем превью из файла документа
                preview_file = 'data:image/png;base64,' + preview_doc.file.decode()
            else:
                # иначе используем дефолтную пикчу (https://commons.wikimedia.org/wiki/File:No_Preview_image_2.png)
                preview_file = 'data:image/png;base64,' + default_preview_b64

            tasks_list.append({
                'task_id': t.task_id,
                'part_id': t.part_id,
                'order_number': t.order_number,
                'order_description': t.order_description,
                'order_status_label': selection_dict.get(t.order_status),
                'order_status_key': t.order_status,
                'taken_on': t.taken_on,
                'done_on': t.done_on,
                'task_description': t.task_description,
                'parts_count': t.parts_count,
                'documents': [{
                    'part_id': d.part_id,
                    'description': d.description,
                    'file': ('data:image/png;base64,' + d.file.decode()) if d.file else None,
                    'filename': d.filename
                } for d in t.documents],
                'preview_file': preview_file,
                'hidden': t.hidden,
                'taken_by_logins': t.taken_by_ids.mapped('login')
            })

        return {
            'tasks_list': tasks_list,
            'no_preview': 'data:image/png;base64,' + default_preview_b64,
            # логин юзера, мб, можно достать и на клиенте, но я для быстроты решения решил сделать так
            'current_user_login': request.env.user.login
        }