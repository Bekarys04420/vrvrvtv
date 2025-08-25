# -*- coding: utf-8 -*-
import os
import json
import random
from threading import Thread
from flask import Flask
import telebot

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN", "8214776143:AAG7GzwSjdF32o8pAQdtFKt_jNv2A7TBilk")

# 2 админ ID
ADMIN_IDS = {7186196783, 7335365453}

START_MONEY = 500000
BONUS_AMOUNT = 77777
DATA_FILE = "users.json"

# Flask (Railway үшін)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

bot = telebot.TeleBot(TOKEN)

# ================= DATA =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data()

def register_user(user_id, username):
    if str(user_id) not in users:
        users[str(user_id)] = {
            "money": START_MONEY,
            "wins": 0,
            "loses": 0,
            "sent": 0,
            "received": 0,
            "clan": None,
            "xp": 0,
            "level": 1,
            "nickname": username
        }
        save_data(users)

# ================= COMMANDS =================

@bot.message_handler(commands=["start"])
def start(msg):
    register_user(msg.from_user.id, msg.from_user.first_name)
    bot.reply_to(msg, f"""Сәлем, біздің “Addiction” Қош келдің💸

Ойын командалары⚙️:

/balance - Өз шотынызды тексеру💳
/profile - Өзініздің профильынызды қарау👤
/givemoney @user (сумма) - Ақша жіберу💸
/list - Бай адамдар тізімі📋
/nick (жаңа ник) - Ник өзгерту
/c (клан аты) - Жаңа клан құру⚔️
/invite @user - Кланға шақыру
/remove @user - Кланнан шығару
/r (клан аты) - Кланға кіру

Админ командалары⚙️:
/gmoney @user (сумма) - Ақша қосу💸
/delmoney @user - Ақшасын жою❌

Эротикалық:
/выебать, трахнуть, секс, пнуть (reply арқылы)

Бонус:
бонус1–6 (әрқайсысы +77777тг)

🤖Ботты жасап шыққан админ: @lliakaiMY 
""")

# Баланс
@bot.message_handler(commands=["balance"])
def balance(msg):
    register_user(msg.from_user.id, msg.from_user.first_name)
    money = users[str(msg.from_user.id)]["money"]
    bot.reply_to(msg, f"💳 Баланс: {money} тг")

# Профиль
@bot.message_handler(commands=["profile"])
def profile(msg):
    u = users[str(msg.from_user.id)]
    bot.reply_to(msg, f"""👤Профиль:
⚙️ID: {msg.from_user.id}
├ Ник: {u['nickname']}
├ Ақша💰: {u['money']}
├ Ұтқандары✅: {u['wins']}
├ Жеңілгендері🛑: {u['loses']}
├ Жіберілген💸: {u['sent']}
├ Алынған💵: {u['received']}
├ Клан⚔️: {u['clan']}
├ Дәреже📈: {u['level']} lvl (XP: {u['xp']}/100)
""")

# Ник өзгерту
@bot.message_handler(commands=["nick"])
def change_nick(msg):
    args = msg.text.split(" ", 1)
    if len(args) < 2:
        return bot.reply_to(msg, "Жаңа ник жазыңыз: /nick ЖаңаНик")
    users[str(msg.from_user.id)]["nickname"] = args[1]
    save_data(users)
    bot.reply_to(msg, f"✅ Ник '{args[1]}' болып өзгертілді!")

# Ақша жіберу
@bot.message_handler(commands=["givemoney"])
def give_money(msg):
    try:
        args = msg.text.split()
        target = msg.reply_to_message.from_user.id if msg.reply_to_message else None
        amount = int(args[-1])
        sender = str(msg.from_user.id)

        if not target:
            return bot.reply_to(msg, "Қолданушыға жауап ретінде жазыңыз.")

        if users[sender]["money"] < amount:
            return bot.reply_to(msg, "Ақша жетпейді!")

        users[sender]["money"] -= amount
        users[sender]["sent"] += amount
        users[str(target)]["money"] += amount
        users[str(target)]["received"] += amount
        save_data(users)

        bot.reply_to(msg, f"✅ Ақша жіберілді! {amount} тг")
    except:
        bot.reply_to(msg, "Қате формат. Мысалы: /givemoney (reply) 10000")

# Бай адамдар тізімі
@bot.message_handler(commands=["list"])
def rich_list(msg):
    top = sorted(users.items(), key=lambda x: x[1]["money"], reverse=True)[:10]
    text = "💸 Ең бай адамдар:\n\n"
    for uid, data in top:
        text += f"{data['nickname']} — {data['money']} тг\n"
    bot.reply_to(msg, text)

# Админ командалары
@bot.message_handler(commands=["gmoney"])
def gmoney(msg):
    if msg.from_user.id not in ADMIN_IDS:
        return
    try:
        target = msg.reply_to_message.from_user.id
        amount = int(msg.text.split()[-1])
        users[str(target)]["money"] += amount
        save_data(users)
        bot.reply_to(msg, f"✅ {amount} тг қосылды!")
    except:
        bot.reply_to(msg, "Қолдану: /gmoney (reply) 10000")

@bot.message_handler(commands=["delmoney"])
def delmoney(msg):
    if msg.from_user.id not in ADMIN_IDS:
        return
    try:
        target = msg.reply_to_message.from_user.id
        users[str(target)]["money"] = 0
        save_data(users)
        bot.reply_to(msg, "❌ Ақшасы жойылды!")
    except:
        bot.reply_to(msg, "Қолдану: /delmoney (reply)")

# Клан жасау
@bot.message_handler(commands=["c"])
def clan_create(msg):
    args = msg.text.split()
    if len(args) < 2:
        return bot.reply_to(msg, "Клан атауын жазыңыз: /c ClanName")
    users[str(msg.from_user.id)]["clan"] = args[1]
    save_data(users)
    bot.reply_to(msg, f"⚔️ Клан құрылды: {args[1]}")

# Invite/remove/r (қарапайым түрде)
@bot.message_handler(commands=["invite"])
def clan_invite(msg):
    if not msg.reply_to_message:
        return bot.reply_to(msg, "Қолданушыға жауап ретінде жазыңыз.")
    target = str(msg.reply_to_message.from_user.id)
    clan = users[str(msg.from_user.id)]["clan"]
    if not clan:
        return bot.reply_to(msg, "Сен кланда емессің!")
    users[target]["clan"] = clan
    save_data(users)
    bot.reply_to(msg, f"{users[target]['nickname']} кланға қосылды: {clan}")

@bot.message_handler(commands=["remove"])
def clan_remove(msg):
    if not msg.reply_to_message:
        return bot.reply_to(msg, "Қолданушыға жауап ретінде жазыңыз.")
    target = str(msg.reply_to_message.from_user.id)
    users[target]["clan"] = None
    save_data(users)
    bot.reply_to(msg, f"{users[target]['nickname']} кланнан шығарылды!")

@bot.message_handler(commands=["r"])
def clan_join(msg):
    args = msg.text.split()
    if len(args) < 2:
        return bot.reply_to(msg, "Қолдану: /r ClanName")
    users[str(msg.from_user.id)]["clan"] = args[1]
    save_data(users)
    bot.reply_to(msg, f"⚔️ Сен {args[1]} кланына кірдің!")

# Бонус
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("бонус"))
def bonus(msg):
    if msg.text.lower() in ["бонус1", "бонус2", "бонус3", "бонус4", "бонус5", "бонус6"]:
        users[str(msg.from_user.id)]["money"] += BONUS_AMOUNT
        save_data(users)
        bot.reply_to(msg, f"🎁 +{BONUS_AMOUNT} тг")
    else:
        bot.reply_to(msg, "Қолдану: бонус1–6")

# Эротикалық
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["выебать", "трахнуть", "секс", "пнуть"])
def erotic(msg):
    if not msg.reply_to_message:
        return bot.reply_to(msg, "Біреудің хабарламасына жауап бер.")
    sender = users[str(msg.from_user.id)]["nickname"]
    target = users[str(msg.reply_to_message.from_user.id)]["nickname"]
    actions = {
        "выебать": f"🥵 {sender} жёстко выебал {target}",
        "трахнуть": f"🔥 {sender} оттрахал {target}",
        "секс": f"💦 {sender} отьебал {target} во все дырочки",
        "пнуть": f"👊 {sender} пнул {target}"
    }
    bot.send_message(msg.chat.id, actions[msg.text.lower()])

# Ойындар (эмодзи)
@bot.message_handler(func=lambda m: any(x in m.text.lower() for x in ["баскетбол", "футбол", "дартс", "боулинг", "казино"]))
def play_game(msg):
    sender = str(msg.from_user.id)
    text = msg.text.lower().split()
    if len(text) < 2: return
    game, amount = text[0], int(text[1])
    emoji = {"баскетбол":"🏀","футбол":"⚽️","дартс":"🎯","боулинг":"🎳","казино":"🎰"}[game]
    sent = bot.send_dice(msg.chat.id, emoji=emoji)
    dice_value = sent.dice.value
    win = random.choice([True, False])
    if win:
        users[sender]["money"] += amount
        users[sender]["wins"] += 1
        result = f"✅ Ұттың! +{amount} тг"
    else:
        users[sender]["money"] -= amount
        users[sender]["loses"] += 1
        result = f"❌ Ұтылдың! -{amount} тг"
    save_data(users)
    bot.send_message(msg.chat.id, f"{result}\nБаланс: {users[sender]['money']} тг")

# ================= RUN =================
if __name__ == "__main__":
    Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
    bot.polling(non_stop=True)
