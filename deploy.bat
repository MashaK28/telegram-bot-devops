@echo off
chcp 65001 >nul
echo  Начало сборки и запуска контейнеров
docker-compose up -d --build
echo  Бот и мониторинг работают
echo  Grafana (графики): http://localhost:3000 (логин: admin, пароль: admin)
echo  Prometheus (цифры): http://localhost:9090
pause