import telebot
import requests
import random
import os
from prometheus_client import start_http_server, Counter

from flask import Flask
import threading

# Создаём Flask приложение для health check от Render
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Bot is running!", 200

@flask_app.route('/health')
def health():
    return {"status": "healthy"}, 200

# Запускаем Flask в отдельном потоке
def run_flask():
    flask_app.run(host='0.0.0.0', port=8001)

# Запускаем Flask перед ботом
threading.Thread(target=run_flask, daemon=True).start()

VISITS_COUNTER = Counter('bot_visits_total', 'Total bot commands used')

token = os.getenv('BOT_TOKEN')

if not token:
    raise ValueError("BOT_TOKEN не найден! Установите переменную окружения BOT_TOKEN")

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    VISITS_COUNTER.inc()
    welcome_text = (
        "Привет! 👋 Я твой помощник для хорошего настроения.\n\n"
        "Вот что я умею:\n"
        "🖼 /picture — пришлю случайную милую картинку\n"
        "📍 /place — посоветую, куда классно сходить\n"
        "🧠 /fact — расскажу интересный факт\n"
        "📜 /poem — расскажу короткое стихотворение"
    )
    bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(commands=['poem'])
def send_poem(message):
    VISITS_COUNTER.inc()
    poems = [
        "Унылая пора! Очей очарованье! Приятна мне твоя прощальная краса... 🍂",
        "Ночь, улица, фонарь, аптека, бессмысленный и тусклый свет... 🌃"
    ]
    bot.send_message(message.chat.id, random.choice(poems))


@bot.message_handler(commands=['picture'])
def send_picture(message):
    VISITS_COUNTER.inc()
    loading_msg = bot.send_message(message.chat.id, "Ищу красивую картинку... 🐈")
    image_files = ['cat1.jpg', 'cat2.jpg', 'cat3.jpg', 'cat4.jpg'] 
    random_image = random.choice(image_files)
    file_path = os.path.join('images', random_image)
    
    try:
        with open(file_path, 'rb') as photo:
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_photo(message.chat.id, photo, caption="Держи порцию милоты из моей коллекции! 😻")
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Ой, картинка потерялась!")


@bot.message_handler(commands=['place'])
def suggest_place(message):
    VISITS_COUNTER.inc()
    places = [
        "🎨 Сходи на мастер-класс по гончарному делу. Это очень медитативно!",
        "☕ Найди уютное антикафе с настольными играми и возьми друга/подругу.",
        "🌳 Устрой вечернюю прогулку по парку или набережной с термосом горячего чая.",
        "🎬 Сходи в кинотеатр на фильм, жанр которого ты обычно не смотришь.",
        "🧩 Посети квест-комнату — это отличный способ проверить свою логику и повеселиться."
    ]
    suggestion = random.choice(places)
    bot.send_message(message.chat.id, f"💡 Идея на сегодня:\n\n{suggestion}")


@bot.message_handler(commands=['fact'])
def send_fact(message):
    VISITS_COUNTER.inc()
    facts = [
        "🐙 У осьминогов три сердца и голубая кровь.",
        "🍯 Мёд — единственный продукт, который не портится. Археологи находили съедобный мёд в гробницах фараонов!",
        "🌍 На Венере день длится дольше, чем год.",
        "🍓 Клубника — это не ягода, а разросшееся цветоложе. А вот банан — ягода!",
        "🦦 Каланы держатся за лапки во сне, чтобы их не унесло течением."
    ]
    bot.send_message(message.chat.id, f"🧠 А ты знал, что:\n\n{random.choice(facts)}")

start_http_server(8000)
bot.polling(none_stop=True)
