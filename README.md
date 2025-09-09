# АСАИ — Тестовое задание — АРМ

## Быстрые ссылки

- 🔗 Этот епозиторий: **[https://github.com/beerurri/asai_awp_test_assignment](https://github.com/beerurri/asai_awp_test_assignment)**  
- 🎥 Демо-видео: **[https://youtu.be/ssGE4TmcM98](https://youtu.be/ssGE4TmcM98)**

## Быстрый старт (Docker Compose)

```bash
git clone [⟨https://github.com/org/repo.git⟩](https://github.com/beerurri/asai_awp_test_assignment)
cd asai_awp_test_assignment
docker compose up
```
Перед `docker-compose up` убедитесь, что запущен Docker Engine. Затем http://127.0.0.1:8069

## Что сделано (далее `~`=`repo dir`)
- Модели списка задач (`awp.tasks`) и документов к ним (`awp.docs`)
- Добавлено несолько демо-пользователей (`~/demo/demo_users.xml`):
  - `user1` и `user2` -- рядовые пользователи,
  - `manager` -- менеджер/технолог/старший_технолог на производстве,
  - `admin` -- админ (не суперпользователь из `base.user_admin`)
- Соответствующие пользователи включены в группы (`~/security/security.xml`):
  - `group_awp_user` -- группа рядовых пользователей,
  - `group_awp_manager` -- группа менеджеров/.../...,
  - `group_awp_admin` -- группа админа/ов
  - ... и добавлены правила доступа к задачам `awp.tasks` и документам `awp.docs`
- Группам прописаны права CRUD (`~/security/ir.model.access.csv`)
- Реализован пользовательский интерфейс с помощью [Odoo QWeb Templates](https://www.odoo.com/documentation/18.0/developer/reference/frontend/qweb.html) и [Bootstrap v5](https://getbootstrap.com/docs/5.0/getting-started/introduction/)

Благодаря такой архитектуре прав доступа Odoo автоматически 
