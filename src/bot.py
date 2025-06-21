"""
Telegram Bot Process for Art Therapist
This bot receives photos from users, analyzes emotions, and provides art therapy recommendations.
"""

import asyncio
import logging
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ML_API_URL = os.getenv('ML_API_URL', 'http://localhost:8001')
LLM_API_URL = os.getenv('LLM_API_URL')
LLM_API_KEY = os.getenv('LLM_API_KEY')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Art therapy recommendations based on emotions
EMOTION_PROMPTS = {
    'angry': """Пользователь испытывает гнев. Предложи ему персонализированные техники арт-терапии для работы с гневом. 
    Включи конкретные упражнения: рисование абстрактных форм, работу с красным цветом, создание коллажей для выражения эмоций. 
    Ответ должен быть поддерживающим, понимающим и практичным. Длина ответа: 150-200 слов.""",
    
    'disgust': """Пользователь испытывает отвращение или неприятие. Предложи техники арт-терапии для работы с этими чувствами.
    Включи упражнения по трансформации негативных образов, работу с текстурами, создание защитных символов.
    Ответ должен быть деликатным и поддерживающим. Длина ответа: 150-200 слов.""",
    
    'fear': """Пользователь испытывает страх или тревогу. Предложи успокаивающие техники арт-терапии.
    Включи упражнения: рисование мандал, работу с мягкими цветами, создание образов безопасности и защиты.
    Ответ должен быть успокаивающим и вселяющим уверенность. Длина ответа: 150-200 слов.""",
    
    'happy': """Пользователь испытывает радость! Предложи техники арт-терапии для усиления и сохранения позитивных эмоций.
    Включи упражнения: создание ярких коллажей, рисование солнечных образов, работу с теплыми цветами.
    Ответ должен быть вдохновляющим и энергичным. Длина ответа: 150-200 слов.""",
    
    'sad': """Пользователь испытывает грусть. Предложи мягкие техники арт-терапии для работы с печалью.
    Включи упражнения: рисование дождя и его трансформации в радугу, работу с синими оттенками, создание образов поддержки.
    Ответ должен быть сочувствующим и обнадеживающим. Длина ответа: 150-200 слов.""",
    
    'surprise': """Пользователь испытывает удивление. Предложи техники арт-терапии для исследования новых эмоций.
    Включи упражнения: экспериментирование с новыми материалами, создание неожиданных цветовых сочетаний.
    Ответ должен быть любопытным и поощряющим исследование. Длина ответа: 150-200 слов.""",
    
    'neutral': """Пользователь находится в нейтральном эмоциональном состоянии. Предложи техники арт-терапии для самопознания.
    Включи упражнения: свободное рисование, создание автопортретов, работу с различными материалами для исследования внутреннего мира.
    Ответ должен быть мягко направляющим и поощряющим самоисследование. Длина ответа: 150-200 слов."""
}

async def call_llm_api(prompt: str) -> str:
    """
    Call LLM API to generate art therapy recommendations
    
    Args:
        prompt: The prompt for the LLM
        
    Returns:
        Generated recommendation text
    """
    if not LLM_API_URL or not LLM_API_KEY:
        # Fallback to predefined responses if no LLM API is configured
        return generate_fallback_response(prompt)
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {LLM_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',  # or another model
                'messages': [
                    {'role': 'system', 'content': 'Ты опытный арт-терапевт, который помогает людям через творчество.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 300,
                'temperature': 0.7
            }
            
            async with session.post(LLM_API_URL, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    logger.error(f"LLM API error: {response.status}")
                    return generate_fallback_response(prompt)
                    
    except Exception as e:
        logger.error(f"Error calling LLM API: {e}")
        return generate_fallback_response(prompt)

def generate_fallback_response(prompt: str) -> str:
    """Generate fallback response when LLM API is not available"""
    if 'гнев' in prompt.lower() or 'angry' in prompt.lower():
        return """Я вижу, что вы испытываете сильные эмоции. Попробуйте технику "Выплеск гнева на бумаге":

🎨 Возьмите большой лист бумаги и яркие краски (особенно красный, оранжевый)
✏️ Рисуйте резкими, энергичными движениями - линии, пятна, абстрактные формы
🖌️ Не думайте о красоте, просто выражайте свои чувства через движение кисти
⚡ После завершения, посмотрите на рисунок и подумайте, что изменилось в ваших ощущениях

Это поможет безопасно выразить гнев и трансформировать его в творческую энергию."""

    elif 'страх' in prompt.lower() or 'fear' in prompt.lower():
        return """Я понимаю, что вы чувствуете тревогу. Попробуйте успокаивающую технику "Мандала безопасности":

🌸 Нарисуйте круг в центре листа
🎨 Заполните его повторяющимися узорами, используя мягкие цвета (голубой, зеленый, фиолетовый)
✨ Добавьте символы, которые ассоциируются у вас с безопасностью и покоем
🕯️ Рисуйте медленно, концентрируясь на дыхании

Эта техника поможет успокоить ум и создать ощущение внутренней стабильности."""

    elif 'грусть' in prompt.lower() or 'sad' in prompt.lower():
        return """Я чувствую вашу печаль. Попробуйте технику "От дождя к радуге":

💧 Начните с рисования дождя синими и серыми цветами
☁️ Изобразите тучи, которые символизируют ваши грустные мысли
🌈 Постепенно добавьте яркие цвета, создавая радугу
☀️ Завершите солнцем, пробивающимся сквозь облака

Этот процесс поможет символически пройти через грусть к надежде и обновлению."""

    else:
        return """Творчество - это прекрасный способ исследовать свои эмоции. Попробуйте технику "Свободное выражение":

🎨 Выберите материалы, которые вас привлекают (краски, карандаши, пастель)
✨ Начните рисовать без конкретной цели, следуя своим импульсам
🌈 Позвольте цветам и формам появляться естественно
💭 Не судите результат, просто наслаждайтесь процессом

Помните: в арт-терапии важен процесс, а не результат. Ваши эмоции имеют право на выражение."""

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Handle /start command"""
    welcome_text = """
🎨 Добро пожаловать в бот "Арт-Терапевт"! 

Я помогу вам исследовать свои эмоции через творчество. Просто отправьте мне фотографию своего рисунка, картины или даже селфи, и я проанализирую ваше эмоциональное состояние и предложу персонализированные техники арт-терапии.

📸 Отправьте фото, чтобы начать!
❓ Используйте /help для получения дополнительной информации.
"""
    await message.answer(welcome_text)

@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """Handle /help command"""
    help_text = """
🆘 Как пользоваться ботом:

1️⃣ Отправьте фотографию:
   • Ваш рисунок или картину
   • Селфи (для анализа эмоций по лицу)
   • Любое изображение, которое отражает ваше состояние

2️⃣ Получите анализ эмоций и персональные рекомендации по арт-терапии

3️⃣ Следуйте предложенным техникам для работы с эмоциями

🎨 Арт-терапия помогает:
   • Выразить сложные эмоции
   • Снизить стресс и тревогу
   • Лучше понять себя
   • Найти внутренние ресурсы

💡 Совет: Не беспокойтесь о качестве рисунка - важен процесс, а не результат!
"""
    await message.answer(help_text)

@dp.message(lambda message: message.photo)
async def handle_photo(message: Message) -> None:
    """Handle photo messages"""
    try:
        # Send "typing" action
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Get the largest photo
        photo = message.photo[-1]
        
        # Download photo
        file_info = await bot.get_file(photo.file_id)
        file_data = await bot.download_file(file_info.file_path)
        
        # Send photo to ML API for emotion analysis
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('file', file_data, filename='photo.jpg', content_type='image/jpeg')
            
            async with session.post(f"{ML_API_URL}/analyze_emotion", data=data) as response:
                if response.status == 200:
                    emotion_result = await response.json()
                    
                    if emotion_result['status'] == 'success':
                        dominant_emotion = emotion_result['dominant_emotion']
                        confidence = emotion_result['confidence']
                        
                        # Generate prompt for LLM
                        prompt = EMOTION_PROMPTS.get(dominant_emotion, EMOTION_PROMPTS['neutral'])
                        
                        # Get art therapy recommendation
                        recommendation = await call_llm_api(prompt)
                        
                        # Format response
                        response_text = f"""
🎭 **Анализ эмоций завершен!**

📊 Доминирующая эмоция: **{dominant_emotion.upper()}**
📈 Уверенность: {confidence:.2%}

🎨 **Персональные рекомендации по арт-терапии:**

{recommendation}

💡 Помните: творчество - это безопасное пространство для выражения любых эмоций!
"""
                        
                        await message.answer(response_text, parse_mode="Markdown")
                        
                    else:
                        # No face detected
                        await message.answer("""
😊 Я не смог определить эмоции на этом изображении, но это не проблема!

🎨 **Универсальные техники арт-терапии:**

Попробуйте технику "Интуитивное рисование":
• Выберите цвета, которые вас сейчас привлекают
• Рисуйте абстрактные формы, следуя внутренним импульсам  
• Не думайте о результате, сосредоточьтесь на процессе
• После завершения подумайте, что вы чувствуете

Творчество помогает лучше понять себя даже без анализа эмоций! 🌈
""")
                else:
                    await message.answer("❌ Произошла ошибка при анализе изображения. Попробуйте еще раз.")
                    
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await message.answer("❌ Произошла ошибка при обработке фотографии. Попробуйте еще раз.")

@dp.message()
async def handle_other_messages(message: Message) -> None:
    """Handle other messages"""
    await message.answer("""
📸 Пожалуйста, отправьте фотографию для анализа эмоций!

Вы можете отправить:
• Свой рисунок или картину
• Селфи для анализа эмоций по лицу
• Любое изображение, отражающее ваше состояние

Используйте /help для получения подробной информации.
""")

async def main() -> None:
    """Main function to run the bot"""
    logger.info("Starting Art Therapist Bot...")
    
    # Check if ML API is available
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ML_API_URL}/health") as response:
                if response.status == 200:
                    logger.info("ML API is available")
                else:
                    logger.warning("ML API is not responding properly")
    except Exception as e:
        logger.error(f"Cannot connect to ML API: {e}")
        logger.warning("Bot will continue without ML API (limited functionality)")
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

