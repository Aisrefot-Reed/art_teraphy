# Руководство по развертыванию

## Системные требования

### Минимальные требования
- **CPU**: 1 ядро, 2 ГГц
- **RAM**: 2 ГБ (4 ГБ для полной версии с TensorFlow)
- **Диск**: 5 ГБ свободного места
- **ОС**: Ubuntu 20.04+, CentOS 7+, или любая Linux с Python 3.11+

### Рекомендуемые требования
- **CPU**: 2+ ядра
- **RAM**: 4+ ГБ
- **Диск**: 10+ ГБ SSD
- **Сеть**: Стабильное интернет-соединение

## Пошаговое развертывание

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Установка дополнительных зависимостей
sudo apt install git curl wget -y
```

### 2. Клонирование проекта

```bash
# Клонирование репозитория
git clone <repository-url>
cd art_therapist_bot

# Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Настройка конфигурации

```bash
# Копирование шаблона конфигурации
cp .env.template .env

# Редактирование конфигурации
nano .env
```

Заполните обязательные поля:
```env
BOT_TOKEN=your_telegram_bot_token_here
ML_API_URL=http://localhost:8001
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=your_openai_api_key_here
```

### 4. Тестирование

```bash
# Тест ML API
cd src
python ml_api_simple.py &
sleep 5
curl http://localhost:8001/health

# Остановка тестового процесса
pkill -f ml_api_simple.py
```

### 5. Настройка автозапуска (systemd)

Создайте файл сервиса для ML API:

```bash
sudo nano /etc/systemd/system/art-therapist-ml.service
```

```ini
[Unit]
Description=Art Therapist ML API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/art_therapist_bot/src
Environment=PATH=/home/ubuntu/art_therapist_bot/venv/bin
ExecStart=/home/ubuntu/art_therapist_bot/venv/bin/python ml_api_simple.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Создайте файл сервиса для Telegram бота:

```bash
sudo nano /etc/systemd/system/art-therapist-bot.service
```

```ini
[Unit]
Description=Art Therapist Telegram Bot
After=network.target art-therapist-ml.service
Requires=art-therapist-ml.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/art_therapist_bot/src
Environment=PATH=/home/ubuntu/art_therapist_bot/venv/bin
ExecStart=/home/ubuntu/art_therapist_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация сервисов:

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable art-therapist-ml.service
sudo systemctl enable art-therapist-bot.service

# Запуск сервисов
sudo systemctl start art-therapist-ml.service
sudo systemctl start art-therapist-bot.service

# Проверка статуса
sudo systemctl status art-therapist-ml.service
sudo systemctl status art-therapist-bot.service
```

## Мониторинг и логирование

### Просмотр логов

```bash
# Логи ML API
sudo journalctl -u art-therapist-ml.service -f

# Логи Telegram бота
sudo journalctl -u art-therapist-bot.service -f

# Логи за последний час
sudo journalctl -u art-therapist-bot.service --since "1 hour ago"
```

### Настройка ротации логов

```bash
sudo nano /etc/logrotate.d/art-therapist
```

```
/var/log/art-therapist/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload art-therapist-ml.service
        systemctl reload art-therapist-bot.service
    endscript
}
```

## Обновление

### Автоматическое обновление

Создайте скрипт обновления:

```bash
nano update.sh
```

```bash
#!/bin/bash

echo "Updating Art Therapist Bot..."

# Остановка сервисов
sudo systemctl stop art-therapist-bot.service
sudo systemctl stop art-therapist-ml.service

# Обновление кода
git pull origin main

# Активация виртуального окружения
source venv/bin/activate

# Обновление зависимостей
pip install -r requirements.txt --upgrade

# Запуск сервисов
sudo systemctl start art-therapist-ml.service
sudo systemctl start art-therapist-bot.service

echo "Update completed!"
```

```bash
chmod +x update.sh
```

### Ручное обновление

```bash
# Остановка сервисов
sudo systemctl stop art-therapist-bot.service
sudo systemctl stop art-therapist-ml.service

# Обновление
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Запуск
sudo systemctl start art-therapist-ml.service
sudo systemctl start art-therapist-bot.service
```

## Резервное копирование

### Создание бэкапа

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/art-therapist"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап конфигурации
cp .env $BACKUP_DIR/env_$DATE
cp -r src/ $BACKUP_DIR/src_$DATE/

# Бэкап логов
sudo cp -r /var/log/art-therapist/ $BACKUP_DIR/logs_$DATE/

echo "Backup created: $BACKUP_DIR"
```

### Восстановление

```bash
# Остановка сервисов
sudo systemctl stop art-therapist-bot.service
sudo systemctl stop art-therapist-ml.service

# Восстановление файлов
cp /backup/art-therapist/env_YYYYMMDD_HHMMSS .env
cp -r /backup/art-therapist/src_YYYYMMDD_HHMMSS/* src/

# Запуск сервисов
sudo systemctl start art-therapist-ml.service
sudo systemctl start art-therapist-bot.service
```

## Безопасность

### Настройка файрвола

```bash
# Установка ufw
sudo apt install ufw -y

# Базовые правила
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Разрешение SSH
sudo ufw allow ssh

# Разрешение только локального доступа к ML API
sudo ufw allow from 127.0.0.1 to any port 8001

# Активация файрвола
sudo ufw enable
```

### Настройка SSL (если требуется внешний доступ)

```bash
# Установка Nginx
sudo apt install nginx -y

# Настройка прокси
sudo nano /etc/nginx/sites-available/art-therapist
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Активация сайта
sudo ln -s /etc/nginx/sites-available/art-therapist /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Установка SSL с Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Производительность

### Оптимизация для production

1. **Используйте Gunicorn для ML API**:

```bash
pip install gunicorn
```

Обновите systemd сервис:
```ini
ExecStart=/home/ubuntu/art_therapist_bot/venv/bin/gunicorn -w 2 -k uvicorn.workers.UvicornWorker ml_api_simple:app --bind 0.0.0.0:8001
```

2. **Настройте кэширование**:

```python
# В ml_api.py добавьте кэширование результатов
from functools import lru_cache

@lru_cache(maxsize=100)
def analyze_cached_emotion(image_hash):
    # Кэширование результатов анализа
    pass
```

3. **Мониторинг ресурсов**:

```bash
# Установка htop для мониторинга
sudo apt install htop -y

# Мониторинг использования памяти
watch -n 5 'free -h && ps aux | grep python'
```

## Устранение неполадок

### Частые проблемы

1. **Сервис не запускается**:
```bash
sudo systemctl status art-therapist-bot.service
sudo journalctl -u art-therapist-bot.service --no-pager
```

2. **Нет доступа к ML API**:
```bash
curl -v http://localhost:8001/health
netstat -tlnp | grep 8001
```

3. **Проблемы с зависимостями**:
```bash
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

4. **Проблемы с правами доступа**:
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/art_therapist_bot
chmod +x start.sh
```

### Диагностика

```bash
# Проверка всех компонентов
./diagnose.sh
```

```bash
#!/bin/bash
# diagnose.sh

echo "=== Art Therapist Bot Diagnostics ==="

echo "1. Checking Python version..."
python3.11 --version

echo "2. Checking virtual environment..."
source venv/bin/activate && python --version

echo "3. Checking ML API..."
curl -s http://localhost:8001/health | jq .

echo "4. Checking services status..."
sudo systemctl is-active art-therapist-ml.service
sudo systemctl is-active art-therapist-bot.service

echo "5. Checking ports..."
netstat -tlnp | grep 8001

echo "6. Checking disk space..."
df -h

echo "7. Checking memory..."
free -h

echo "=== Diagnostics completed ==="
```

---

Это руководство покрывает основные аспекты развертывания и поддержки бота в production среде.

