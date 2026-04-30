import os

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8664146267:AAHnfTtoEChAWxH7hL1wZcBVSOKOt8CJhxs"
SHEET_ID = "15NYmrZj1ZU3OofeRWzd20tUEZNpOiFidXAcQ0v5WcU4"
# ================

bot = telebot.TeleBot(BOT_TOKEN)

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet("Заказы")

# Хранилище сессий
user_data = {}

def ask_question(chat_id, question, field):
    user_data[chat_id] = user_data.get(chat_id, {})
    user_data[chat_id]["current_question"] = field
    bot.send_message(chat_id, question)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    bot.send_message(chat_id, "Привет! Я помогу оформить заказ на ремонт ПК/ноутбука. Отвечайте на вопросы.")
    ask_question(chat_id, "1️⃣ Опишите проблему (что случилось, какие признаки):", "problem")

@bot.message_handler(func=lambda m: True)
def handle_answer(message):
    chat_id = message.chat.id
    if chat_id not in user_data or "current_question" not in user_data[chat_id]:
        bot.send_message(chat_id, "Напишите /start для нового заказа")
        return

    field = user_data[chat_id]["current_question"]
    user_data[chat_id][field] = message.text

    if field == "problem":
        ask_question(chat_id, "2️⃣ Модель устройства (ноутбук/ПК, производитель, модель):", "model")
    elif field == "model":
        ask_question(chat_id, "3️⃣ Срочность (обычный / срочно / очень срочно):", "urgency")
    elif field == "urgency":
        ask_question(chat_id, "4️⃣ Выезд к вам или привезёте в мастерскую? (выезд/мастерская):", "service_type")
    elif field == "service_type":
        ask_question(chat_id, "5️⃣ Ваш телефон для связи:", "phone")
    elif field == "phone":
        data = user_data[chat_id]
        order_id = f"PC{datetime.now().strftime('%Y%m%d%H%M%S')}"
        row = [
            order_id,
            str(datetime.now()),
            message.chat.username or "нет_username",
            data["problem"],
            data["model"],
            data["urgency"],
            data["service_type"],
            data["phone"],
            "Новый"
        ]
        sheet.append_row(row)

        if data["urgency"].lower() in ["срочно", "очень срочно"]:
            priority = "🔥 ВЫСОКИЙ ПРИОРИТЕТ"
        else:
            priority = "✅ Обычный"

        bot.send_message(chat_id, f"✅ Заказ {order_id} принят!\n{priority}\nСкоро с вами свяжется мастер.")
        del user_data[chat_id]

print("Бот запущен и работает...")
bot.infinity_polling()
