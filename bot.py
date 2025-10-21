
import telebot
from telebot import types
import time
import json
import os
import threading

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

SAVE_FILE = 'clicker_data.json'
users = {}

# === Завантаження даних ===
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, 'r') as f:
        try:
            users = json.load(f)
        except:
            users = {}

# === Збереження даних ===
def save_data():
    with open(SAVE_FILE, 'w') as f:
        json.dump(users, f)

# === Автоклік (фоновий потік) ===
def auto_click_loop():
    while True:
        for uid in list(users.keys()):
            u = users[uid]
            if u.get('autoclick', False):
                u['clicks'] += 5
                u['total_clicks'] += 5
        save_data()
        time.sleep(3)

threading.Thread(target=auto_click_loop, daemon=True).start()

# === /start ===
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    if uid not in users:
        users[uid] = {
            'clicks': 0,
            'total_clicks': 0,
            'pumpkins': 0,
            'multiplier': 1,
            'pumpkin_mult': 1,
            'title': None,
            'autoclick': False,
            'last_click': 0
        }
        save_data()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🖱 Клік', '🛒 Магазин', '📊 Статистика', '🏆 Топ')
    bot.send_message(uid, "👋 Привіт! Натискай «🖱 Клік» щоб заробляти кліки!", reply_markup=markup)

# === Головна логіка ===
@bot.message_handler(func=lambda m: True)
def handle(message):
    uid = str(message.chat.id)
    if uid not in users:
        return start(message)

    u = users[uid]
    text = message.text

    # === Клік ===
    if text == '🖱 Клік':
        now = time.time()
        if now - u['last_click'] < 1:
            bot.send_message(uid, "⏳ Зачекай 1 секунду перед наступним кліком!")
            return

        u['clicks'] += u['multiplier']
        u['total_clicks'] += u['multiplier']
        u['last_click'] = now

        # 🎃 Кожні 15 кліків = 1 гарбуз
        if u['total_clicks'] % 15 == 0:
            u['pumpkins'] += 1 * u['pumpkin_mult']
            bot.send_message(uid, f"🎃 Ти отримав гарбуз! У тебе тепер {u['pumpkins']} 🎃")

        save_data()
        bot.send_message(uid, f"🖱 Кліків: {u['clicks']} | 🎃 Гарбузів: {u['pumpkins']}")

    # === Магазин ===
    elif text == '🛒 Магазин':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('💥 Купити x2 кліки (100 кліків)')
        markup.add('🎃 Купити x2 гарбузи (100 гарбузів)')
        markup.add('🤖 Автоклік (1000 кліків)')
        markup.add('👑 Купити титул (10000 гарбузів)')
        markup.add('🔙 Назад')
        bot.send_message(uid, "🛒 Магазин:\nВибери, що хочеш купити:", reply_markup=markup)

    # === Покупки ===
    elif text == '💥 Купити x2 кліки (100 кліків)':
        if u['clicks'] >= 100:
            u['clicks'] -= 100
            u['multiplier'] *= 2
            save_data()
            bot.send_message(uid, f"✅ Ти купив x2 кліки! Новий множник: x{u['multiplier']}")
        else:
            bot.send_message(uid, "❌ Недостатньо кліків!")

    elif text == '🎃 Купити x2 гарбузи (100 гарбузів)':
        if u['pumpkins'] >= 100:
            u['pumpkins'] -= 100
            u['pumpkin_mult'] *= 2
            save_data()
            bot.send_message(uid, f"✅ Тепер ти отримуєш вдвічі більше 🎃!\nМножник гарбузів: x{u['pumpkin_mult']}")
        else:
            bot.send_message(uid, "❌ Недостатньо гарбузів!")

    elif text == '🤖 Автоклік (1000 кліків)':
        if u['clicks'] >= 1000:
            u['clicks'] -= 1000
            u['autoclick'] = True
            save_data()
            bot.send_message(uid, "🤖 Ти купив автоклік! Тепер отримуєш +5 кліків кожні 3 секунди!")
        else:
            bot.send_message(uid, "❌ Недостатньо кліків!")

⚝передоз сна⚝ [SK], [21.10.2025 17:42]
elif text == '👑 Купити титул (10000 гарбузів)':
        if u['pumpkins'] >= 10000:
            u['pumpkins'] -= 10000
            u['title'] = "👑 Майстер гарбузів"
            save_data()
            bot.send_message(uid, "👑 Вітаю! Ти отримав титул «Майстер гарбузів»!")
        else:
            bot.send_message(uid, "❌ Недостатньо гарбузів!")

    # === Статистика ===
    elif text == '📊 Статистика':
        bot.send_message(uid,
                         f"📊 Статистика:\n"
                         f"🖱 Кліків: {u['clicks']}\n"
                         f"🎃 Гарбузів: {u['pumpkins']}\n"
                         f"💥 Множник кліків: x{u['multiplier']}\n"
                         f"🎃 Множник гарбузів: x{u['pumpkin_mult']}\n"
                         f"🤖 Автоклік: {'✅' if u['autoclick'] else '❌'}\n"
                         f"👑 Титул: {u['title'] if u['title'] else '—'}")

    # === Топ гравців ===
    elif text == '🏆 Топ':
        sorted_users = sorted(users.items(), key=lambda x: x[1].get('total_clicks', 0), reverse=True)
        top_list = ""
        for i, (uid2, data) in enumerate(sorted_users[:10], start=1):
            name = bot.get_chat(uid2).first_name
            top_list += f"{i}. {name} — {data['total_clicks']} кліків\n"
        bot.send_message(uid, "🏆 Топ-10 гравців:\n" + top_list)

    # === Назад ===
    elif text == '🔙 Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('🖱 Клік', '🛒 Магазин', '📊 Статистика', '🏆 Топ')
        bot.send_message(uid, "🔙 Повернення в головне меню.", reply_markup=markup)


# === Безкінечний цикл (бот працює завжди) ===
while True:
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"Помилка: {e}")
        time.sleep(5)
