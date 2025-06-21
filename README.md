# Телеграм-бот "Арт-Терапевт"

Интеллектуальный Telegram-бот, который анализирует эмоции на фотографиях пользователей и предоставляет персонализированные рекомендации по арт-терапии с использованием языковых моделей.

## 🎯 Возможности

- **Анализ эмоций**: Определение эмоционального состояния по фотографиям лица или рисункам
- **Персонализированные рекомендации**: Генерация индивидуальных советов по арт-терапии на основе обнаруженных эмоций
- **Поддержка LLM**: Интеграция с внешними API языковых моделей (OpenAI, Claude и др.)
- **Fallback режим**: Работа с предустановленными ответами при отсутствии LLM API
- **Простая архитектура**: Два независимых процесса для легкого масштабирования

## 🏗️ Архитектура

Проект состоит из двух независимых Python-процессов:

1. **ML API Process** (`ml_api.py`) - FastAPI сервис для анализа эмоций
2. **Bot Process** (`bot.py`) - Telegram бот на aiogram

```
Пользователь → Telegram → Bot Process → ML API → LLM API → Ответ пользователю
```

## 📋 Требования

- Python 3.11+
- Telegram Bot Token
- (Опционально) API ключ для языковой модели

## 🚀 Быстрый старт

### 1. Клонирование и установка

```bash
git clone <repository-url>
cd art_therapist_bot
pip install -r requirements.txt
```

### 2. Настройка окружения

Скопируйте файл конфигурации и заполните необходимые данные:

```bash
cp .env.template .env
```

Отредактируйте `.env` файл:

```env
# Обязательные параметры
BOT_TOKEN=your_telegram_bot_token_here

# ML API (обычно не требует изменений)
ML_API_URL=http://localhost:8001

# Опциональные параметры для LLM API
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=your_openai_api_key_here
```

### 3. Получение Telegram Bot Token

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env` файл

### 4. Запуск

Используйте скрипт автоматического запуска:

```bash
chmod +x start.sh
./start.sh
```

Или запустите процессы вручную:

```bash
# Терминал 1: ML API
cd src
python ml_api_simple.py

# Терминал 2: Telegram Bot
cd src
python bot.py
```

## 📖 Использование

### Команды бота

- `/start` - Приветствие и инструкции
- `/help` - Подробная справка по использованию

### Отправка фотографий

1. Отправьте боту фотографию:
   - Селфи для анализа эмоций по лицу
   - Рисунок или картину
   - Любое изображение, отражающее ваше состояние

2. Получите анализ эмоций и персональные рекомендации по арт-терапии

### Пример взаимодействия

```
Пользователь: [отправляет фото]
Бот: 
🎭 Анализ эмоций завершен!
📊 Доминирующая эмоция: HAPPY
📈 Уверенность: 87%

🎨 Персональные рекомендации по арт-терапии:
[Персонализированный совет на основе LLM]
```



## 🔧 API Документация

### ML API Endpoints

#### GET `/health`
Проверка состояния ML API

**Ответ:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "message": "ML API is ready to process images"
}
```

#### POST `/analyze_emotion`
Анализ эмоций на изображении

**Параметры:**
- `file` (multipart/form-data) - Файл изображения

**Ответ при успехе:**
```json
{
  "status": "success",
  "dominant_emotion": "happy",
  "emotions": {
    "angry": 0.02,
    "disgust": 0.01,
    "fear": 0.03,
    "happy": 0.87,
    "sad": 0.02,
    "surprise": 0.03,
    "neutral": 0.02
  },
  "confidence": 0.87
}
```

**Ответ при отсутствии лица:**
```json
{
  "status": "no_face_detected",
  "message": "No face detected in the image",
  "dominant_emotion": "neutral",
  "emotions": {}
}
```

### Поддерживаемые эмоции

- `angry` - Гнев
- `disgust` - Отвращение  
- `fear` - Страх
- `happy` - Радость
- `sad` - Грусть
- `surprise` - Удивление
- `neutral` - Нейтральное состояние

## 🔌 Интеграция с LLM API

### Поддерживаемые провайдеры

#### OpenAI
```env
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=sk-...
```

#### Anthropic Claude
```env
LLM_API_URL=https://api.anthropic.com/v1/messages
LLM_API_KEY=sk-ant-...
```

### Fallback режим

Если LLM API недоступен, бот использует предустановленные ответы для каждой эмоции:

- Качественные рекомендации по арт-терапии
- Конкретные техники и упражнения
- Поддерживающие сообщения

## 🛠️ Разработка

### Структура проекта

```
art_therapist_bot/
├── src/
│   ├── ml_api.py              # Основной ML API (с FER)
│   ├── ml_api_simple.py       # Упрощенный ML API (для тестирования)
│   └── bot.py                 # Telegram бот
├── requirements.txt           # Python зависимости
├── .env.template             # Шаблон конфигурации
├── start.sh                  # Скрипт запуска
└── README.md                 # Документация
```

### Переключение между ML API

Для использования полноценного анализа эмоций (требует больше ресурсов):
```bash
cd src
python ml_api.py  # Вместо ml_api_simple.py
```

Для тестирования с mock-данными:
```bash
cd src
python ml_api_simple.py
```

### Добавление новых эмоций

1. Обновите список `EMOTIONS` в `ml_api.py`
2. Добавьте соответствующий промпт в `EMOTION_PROMPTS` в `bot.py`
3. Добавьте fallback ответ в функцию `generate_fallback_response`

### Кастомизация ответов

Отредактируйте словарь `EMOTION_PROMPTS` в `bot.py` для изменения промптов, отправляемых в LLM API.

## 🚀 Деплой

### Локальный деплой

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка окружения
cp .env.template .env
# Отредактируйте .env

# Запуск
./start.sh
```

### Docker (опционально)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["./start.sh"]
```

### Облачный деплой

Рекомендуемые платформы:
- **Heroku** - простой деплой с Procfile
- **Railway** - автоматический деплой из Git
- **DigitalOcean App Platform** - масштабируемое решение
- **AWS/GCP/Azure** - для enterprise решений

## 🔒 Безопасность

### Рекомендации

1. **Никогда не коммитьте .env файлы** в репозиторий
2. **Используйте переменные окружения** для production
3. **Ограничьте доступ к ML API** (например, через firewall)
4. **Регулярно обновляйте зависимости** для устранения уязвимостей
5. **Мониторьте использование API** для предотвращения злоупотреблений

### Переменные окружения для production

```bash
export BOT_TOKEN="your_bot_token"
export LLM_API_KEY="your_llm_api_key"
export ML_API_URL="http://localhost:8001"
```

## 🐛 Устранение неполадок

### Частые проблемы

#### Бот не отвечает
1. Проверьте правильность `BOT_TOKEN`
2. Убедитесь, что ML API запущен и доступен
3. Проверьте логи обоих процессов

#### ML API не запускается
1. Убедитесь, что все зависимости установлены
2. Проверьте, что порт 8001 свободен
3. Для полной версии убедитесь, что установлен TensorFlow

#### LLM API не работает
1. Проверьте правильность API ключа
2. Убедитесь в наличии средств на аккаунте
3. Бот будет работать с fallback ответами

### Логирование

Включите подробное логирование для отладки:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Мониторинг

Рекомендуемые метрики для мониторинга:
- Время ответа ML API
- Количество обработанных изображений
- Ошибки LLM API
- Активность пользователей

## 📄 Лицензия

MIT License - см. файл LICENSE для подробностей.

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте раздел "Устранение неполадок"
2. Создайте Issue в GitHub репозитории
3. Опишите проблему максимально подробно

---

**Создано с ❤️ для помощи людям через арт-терапию**

