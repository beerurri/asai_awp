from odoo import models, fields, api

class AsaiAWPTasks(models.Model):
    _name = 'awp.tasks'
    _description = 'ASAI AWP Tasks Model'

    # ИД задачи
    task_id = fields.Char(string='Task ID', requried=True)
    # ИД детали, которую обрабатывают в этой задаче
    part_id = fields.Char(string='Part ID', required=True)
    # номер заказа (integer, unique)
    order_number = fields.Integer(string='Order #', requried=True)
    # описание заказа (например, "диван Иван белый")
    order_description = fields.Text(string='Order description')
    # статус заказа
    order_status = fields.Selection(
        string='Status', 
        selection = [
            ('draft', 'Готово к работе'),
            ('in_progress', 'В работе'),
            ('done', 'Готово'),
            ('defect', 'Брак')
        ],
        default = 'draft',
        required = True
    )

    # datetime, когда взяли заказ в работу (последний раз, если несоклько исполнителей)
    taken_on = fields.Datetime(string='Taken to work on', default=None)
    # datetime, когда заказ готов
    done_on = fields.Datetime(string='Done on', default=None)

    # описание задач в заказе (например, "вырезать")
    task_description = fields.Text(string='Task description')
    # количество деталей, подлежащих обработке
    parts_count = fields.Integer(string='Parts #', required=True)
    # документы к заказу (чертежи и т.п.)
    documents = fields.One2many('awp.docs', string='Documents', compute='_compute_documents')
    # скрыта ли уже задача (возможно только после того, как она готова)
    hidden = fields.Boolean(string='Already hidden or not', default=False)
    # причина брака (текст, указываемый при помечении детали как бракованной)
    defect_reason = fields.Text(string='Defect reason')
    # список пользователей, имеющих доступ (видимость) задачи
    assigned_user_ids = fields.Many2many('res.users', 'awp_tasks_assigned_users_rel', 'task_id', 'user_id', string='Assigned Users')
    # "список" тех, кем взята в работу задача
    taken_by_ids = fields.Many2many('res.users', 'awp_tasks_taken_by_users_rel', 'task_id', 'user_id', string='Task taken by')

    # ограничение по уникальности task_id
    _sql_constraints = [
        ('unique_task_id', 'unique(task_id)', 'Task ID must be unique!')
    ]


    # computed field с документами к этой задаче, документы хранятся в модели AsaiAWPDocs ниже
    @api.depends('part_id')
    def _compute_documents(self):
        for task in self:
            # ищем по part_id, т.к. детали уникальны, а заказов с одинаковыми деталями может быть несколько
            task.documents = self.env['awp.docs'].search([('part_id', '=', task.part_id)])


class AsaiAWPDocs(models.Model):
    _name = 'awp.docs'
    _description = 'ASAI AWP Docs Model'

    # задачи, связанные с этим документом детали
    task_ids = fields.Many2many('awp.tasks', string='Tasks with this part', compute='_compute_task_ids', store=True)
    # ИД детали, связанной с этим документом -- может быть не уникальным,
    # т.к. у одной детали может быть несколько документов
    part_id = fields.Char(string='Part ID', required=True)
    # описание документа/файла
    description = fields.Char(string='Part description')
    # файл в БД
    file = fields.Binary(string='File content', attachment=True, required=True)
    # имя файла
    filename = fields.Char(string='Filename')
    # применяется ли этот документ как превью в списке задач
    preview = fields.Boolean(string='Preview file or not', default=False)

    # уникальное имя файла (очевидно)
    _sql_constraints = [
        ('unique_filename', 'unique(filename)', 'Filename must be unique!')
    ]


    # аналогично computed field задач, но наоборот
    @api.depends('part_id')
    def _compute_task_ids(self):
        for doc in self:
            doc.task_ids = self.env['awp.tasks'].search([('part_id', '=', doc.part_id)])