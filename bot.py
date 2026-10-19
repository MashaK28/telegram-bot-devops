import telebot
import random
import os
import threading
from flask import Flask
import psutil
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Gauge
import time


flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Bot is running!", 200

@flask_app.route('/health')
def health():
    return {"status": "healthy"}, 200

@flask_app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


def run_flask():
    port = int(os.getenv('PORT', 8000))
    flask_app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()


VISITS_COUNTER = Counter('bot_visits_total', 'Total bot commands used')

DISK_USAGE = Gauge('bot_disk_usage_bytes', 'Disk usage in bytes')
DISK_TOTAL = Gauge('bot_disk_total_bytes', 'Total disk space in bytes')
DISK_FREE = Gauge('bot_disk_free_bytes', 'Free disk space in bytes')

token = os.getenv('BOT_TOKEN')

if not token:
    raise ValueError("BOT_TOKEN не найден!")

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

def update_resource_metrics():
    while True:
        try:
            disk = psutil.disk_usage('/')
            DISK_USAGE.set(disk.used)
            DISK_TOTAL.set(disk.total)
            DISK_FREE.set(disk.free)
        except Exception as e:
            print(f"Ошибка обновления метрик диска: {e}")
        time.sleep(15)
threading.Thread(target=update_resource_metrics, daemon=True).start()

if __name__ == "__main__":
    while True:
    try:
        print("Запуск polling...")
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Ошибка polling: {e}")
        print("Перезапуск через 5 секунд")
        time.sleep(5)
