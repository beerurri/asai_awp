/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

export class AWPClientAction extends Component {
    static template = "asai_awp.tasks_list_client_action";
    
    setup() {
        this.state = useState({
            no_preview: "", // храним один экземпляр пикчи в base64 на случай, если где-то нет превью
            tasks: [] // список задач
        });

        // подключаемся к "шине" для обновлений клиентов "на лету"
        this.busService = useService("bus_service");
        this.busService.addChannel('task_update');

        this.busService.subscribe('task_update', (task_updated) => {
            console.log('task_updated: ', task_updated);
            // ищем задачу, которая обновилась на сервере
            let task = this.state.tasks.find(t => t.task_id === task_updated.task_id);
            if (task) {
                // если задача в списке есть, обновляем её поля
                Object.assign(task, task_updated.fields);
                // костыль, потому что в /static/src/xml/tasks_template.xml в qweb template'е
                // t-if="current_user_login not in taken_by_logins"
                // и
                // t-if="current_user_login in taken_by_logins"
                // не работают (cannot read properties of undefined -- taken_by_logins)
                this.state.tasks.map(t => {
                    t.taken_by_logins.includes(this.state.current_user_login) ? t.is_to_take = false : t.is_to_take = true
                });
            }
        });

        onWillStart(async () => {
            console.log('fetching tasks...');
            // достаём список задач
            let resp = await rpc('/awp/tasks-json');
            this.state.tasks = resp.tasks_list;
            this.state.no_preview = resp.no_preview;
            this.state.current_user_login = resp.current_user_login;
            // тот же самый костыль из-за нерабочего qweb template
            this.state.tasks.map(t => {
                t.taken_by_logins.includes(this.state.current_user_login) ? t.is_to_take = false : t.is_to_take = true
            });
            console.log('fetched!');
            console.log(resp);
        });
    }

    // название говорит само за себя
    async onTake(task) {
        console.log("Взять в работу:", task.order_number);
        let res = await rpc('/awp/task-take', { task_id: task.task_id });
        console.log(res);

        if (res.success) {
            this.state.tasks = this.state.tasks.map(t =>
                t.task_id === task.task_id ? { ...t,
                    order_status_key: res.new_status_key,
                    order_status_label: res.new_status_label,
                    taken_on: res.taken_on
                } : t
            );
        }
    }

    // название говорит само за себя (открыть модалку с файлами)
    // здесь заюзал не js-bootstrap для разнообразия
    onFiles(task) {
        console.log("Файлы:", task.order_number);
        const filesModalBody = document.getElementById('filesModalBody');
        filesModalBody.innerHTML = `
            <div class="container mt-4 task-list-container">
                ${task.documents.map(d => `
                    <div class="card mb-3 shadow-sm">
                        <div class="d-flex">
                            <div class="task-img-wrapper">
                                <img src="${d.filename && d.filename.endsWith('.png') ? d.file : this.state.no_preview}"
                                    alt="preview"
                                    class="task-img"/>
                            </div>
                            <div class="card-body d-flex flex-column justify-content-between">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>
                                        <h5 class="card-title">Деталь ${d.part_id}</h5>
                                        <h5 class="card-title">Файл</h5>
                                        <p>${d.filename}</p>
                                        <h5 class="card-title">Описание:</h5>
                                        <p>${d.description}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // при нажатии на "подробнее", без понятия что там отображать. Пусть будет.
    onDetails(task) {
        console.log("Подробнее:", task.order_number);
    }

    // название говорит само за себя
    async onDone(task) {
        console.log("Готово:", task.order_number);
        let res = await rpc('/awp/task-done', { task_id: task.task_id });
        console.log(res);

        if (res.success) {
            this.state.tasks = this.state.tasks.map(t =>
                t.task_id === task.task_id ? { ...t,
                    order_status_key: res.new_status_key,
                    order_status_label: res.new_status_label,
                    done_on: res.done_on
                } : t
            );
        }
    }

    // открыть модалку для ввода описания причины дефекта
    // здесь уже js-bootstrap, тоже для разнообразия
    openDefectModal(task) {
        console.log('Брак', task);

        // очистить содержимое textarea
        document.getElementById('defectModalText').value = "";
        document.getElementById('defectModalOrderId').innerText = `Причина брака заказа  ${task.task_id}`;
        
        const modalEl = document.getElementById('defectModal');
        console.log(modalEl);
        this.defectModal = new bootstrap.Modal(modalEl);
        this.defectModal.show();

        this.currentTask = task;
    }

    // название говорит само за себя
    async sendDefectReason() {
        console.log('Отправить причину брака', this.currentTask);

        if (!this.currentTask) return;

        const reason = document.getElementById('defectModalText').value;
        
        let res = await rpc('/awp/task-defect', {
            task_id: this.currentTask.task_id,
            defect_reason: reason
        });
        console.log(res);

        if (res.success) {
            this.defectModal.hide();
            this.state.tasks = this.state.tasks.map(t =>
                t.task_id === this.currentTask.task_id ? { ...t,
                    order_status_key: res.new_status_key,
                    order_status_label: res.new_status_label,
                    defect_reason: res.defect_reason
                } : t
            );
        } else {
            document.getElementById('warningErrorModalTitle').innerText = `Заказ ${this.currentTask.task_id}`
            document.getElementById('warningErrorModalBody').innerText = 'Не удалось сохранить причину брака';
        }
    }

    // название говорит само за себя
    async onHide(task) {
        console.log("Скрыть:", task.order_number);
        let res = await rpc('/awp/task-hide', { task_id: task.task_id });
        console.log(res);

        if (res.success) {
            this.state.tasks = this.state.tasks.map(t =>
                t.task_id === task.task_id ? { ...t,
                    hidden: res.new_hidden
                } : t
            );
        }
    }
}

registry.category("actions").add("awp.tasks.action", AWPClientAction);