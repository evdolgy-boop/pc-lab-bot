import os
import threading
from flask import Flask
from pc_bot import bot

# Создаём веб-сервер для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

# Запускаем бота в отдельном потоке, чтобы Flask тоже работал
def run_bot():
    print("Запускаем бота...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем Flask-сервер
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)