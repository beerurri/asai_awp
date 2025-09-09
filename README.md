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
- Добавлено несолько демо-пользователей:
  - `user1` и `user2` -- рядовые пользователи,
  - `manager` -- менеджер/технолог/старший_технолог на производстве,
  - `admin` -- админ (не суперпользователь из `base.user_admin`)
- Права и группы пользователей
