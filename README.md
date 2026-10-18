# Бот телеграмм

## 1. Ссылки

https://t.me/noMMMber1_bot - ссылка на тг бота

https://prometheus-f0dl.onrender.com/query - prometheus для отслеживания ресурсов, хэлсчека, бизнес метрик

## 2. Описание файлов проекта

bot.py - Основной код Telegram-бота на Python. Содержит обработчики команд (/start, /picture, /fact, /poem, /place), интеграцию с Prometheus для сбора метрик, Flask-сервер для health check и отдачи метрик

requirements.txt - Список Python-библиотек, необходимых для работы бота: pyTelegramBotAPI (работа с Telegram), prometheus-client (сбор метрик), flask (health check), psutil (мониторинг ресурсов)

Dockerfile - Инструкция для сборки Docker-образа. Определяет базовый образ, устанавливает зависимости, копирует код и настраивает health check для автоматической проверки работоспособности контейнера

docker-compose.yml - Файл для запуска всех сервисов одной командой. Определяет 4 контейнера: бот, Prometheus (сбор метрик), Grafana (визуализация), cAdvisor (мониторинг ресурсов Docker), которое выводит данные при создании докер контейнера на этапе запуска на локальном компьютере (было собрано и проверено на локальном компьютере)

prometheus.yml - Конфигурация Prometheus. Указывает, откуда собирать метрики (адрес бота), как часто опрашивать (каждые 15 секунд) и какие job names использовать

images/ - Папка с картинками (cat1.jpg, cat2.jpg, cat3.jpg, cat4.jpg), которые бот отправляет по команде /picture

CI/CD: файл .github/workflows/deploy.yml - Скрипт GitHub Actions для автоматического деплоя. При каждом push в ветку main автоматически собирает Docker-образ и деплоит на сервер Render.com.

.gitignore - Указывает Git, какие файлы игнорировать (.env с токеном бота, временные файлы Python). Защищает секретные данные от попадания в репозиторий.

файл prometheus/Dockerfile - Создаёт кастомный образ Prometheus, который настроен на сбор метрик с бота

prometheus/prometheus.yml - Настраивает Prometheus на опрос бота каждые 15 секунд, используется для локального мониторинга


## 3. Работа программы

Для локальной разработки и тестирования используется Docker Compose. При выполнении команды запуска (двойной клик по deploy.bat), система разворачивает 4 связанных контейнера в одной сети:

Telegram Bot (основной код)

Prometheus (сборщик метрик)

Grafana (визуализация данных)

cAdvisor (мониторинг ресурсов самих Docker-контейнеров)

<img width="1588" height="654" alt="image" src="https://github.com/user-attachments/assets/a779f830-c3dd-4c8d-845c-bd4fb4f72eaa" />


В терминал выводятся локалхосты по которым можно перейти на тот или иной контейнер:

<img width="1898" height="564" alt="image" src="https://github.com/user-attachments/assets/500d3c05-7eee-4f69-973b-07e1717e01c2" />


По адресу http://localhost:3000 (Grafana): Открывается панель управления. После входа (admin/admin), там готовые дашборды с графиками: количество вызовов команд бота в час, потребление оперативной памяти (RAM) и нагрузки на процессор (CPU).

По адресу http://localhost:9090 (Prometheus): Открывается интерфейс базы данных метрик

По адресу http://localhost:8080 (cAdvisor): Видим статистику по каждому запущенному контейнеру: точное использование ядер CPU, мегабайт памяти и сетевого трафика в реальном времени.


Чтобы бот работал 24/7 и был доступен пользователям, код был отправлен в репозиторий GitHub, откуда сработал CI/CD пайплайн. Он автоматически собрал Docker-образ (артефакт) и развернул его на облачной платформе Render.com. Для имитации реальных производственных условий мониторинг (Prometheus) был вынесен в отдельный контур. В результате в облаке Render.com развернуто два независимых, но связанных сервиса, код и конфигурация которых управляются через единый репозиторий GitHub.

<img width="1524" height="726" alt="image" src="https://github.com/user-attachments/assets/cde65ff9-f706-4140-8f37-f8041a65de8f" />


## 4. Работа с Prometheus

После перехода по ссылке, переходим на вкладку Graph, и, вводим след.команды:

bot_visits_total - Общее количество помещений бота

<img width="1879" height="906" alt="image" src="https://github.com/user-attachments/assets/02ac626b-5ce2-42c2-b885-16393c5d2b31" />


rate(bot_visits_total[1h]) - Команды в час

<img width="1847" height="782" alt="image" src="https://github.com/user-attachments/assets/7d3acc2f-86b1-46c7-967b-139d7c5be8e5" />


up{job="telegram_bot"} - Статус бота (Health Check) если 1 - рабочая программа, если 0 - бот не работает

<img width="1864" height="915" alt="image" src="https://github.com/user-attachments/assets/aa1926fc-c70b-4364-9a49-de1c755429d0" />


process_resident_memory_bytes / 1024 / 1024 - Потребление RAM (МБ)

<img width="1889" height="889" alt="image" src="https://github.com/user-attachments/assets/29cb4f4b-9363-40bf-a42e-db8cb14434b0" />


rate(process_cpu_seconds_total[1m]) * 100 - Нагрузка CPU (%)

<img width="1856" height="900" alt="image" src="https://github.com/user-attachments/assets/aeabc533-099a-4977-83e7-2b34603435d4" />


bot_disk_usage_bytes / 1024 / 1024 - Потребление диска (МБ)

<img width="1877" height="896" alt="image" src="https://github.com/user-attachments/assets/9cbe329c-c086-4a8b-8ad8-8cbf32538b22" />
