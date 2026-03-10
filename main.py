import asyncio
import logging
import sqlite3
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.markdown import hbold

# 🌐 СЕРВЕРИ "БЕДОРКУНАК" (FLASK KEEP ALIVE)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive! 24/7"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    # Логҳои Flask-ро кам мекунем, то ба кори бот халал нарасонанд
    import logging as flask_logging
    log = flask_logging.getLogger('werkzeug')
    log.setLevel(flask_logging.ERROR)
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_web_server)
    t.start()
# ==========================================

# Токени боти шумо
BOT_TOKEN = "8547728417:AAHIgCXJFjmEEyinLMr7wpiXAWHtOGnQjlY"

dp = Dispatcher()

# Пайвастшавӣ ба базаи маълумот барои сабти корбарон
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
conn.commit()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    # Сабт кардани ID-и корбар ба база
    user_id = message.from_user.id
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    except Exception as e:
        logging.error(f"Хатогӣ дар сабти база: {e}")

    user_name = message.from_user.first_name

    welcome_text = (
        f"👋 Здравствуйте, {hbold(user_name)}!\n\n"
        f"Добро пожаловать в 🌌 {hbold('TonMineSpace')} — вашу передовую платформу для облачного майнинга TON прямо в Telegram.\n\n"
        f"🚀 {hbold('О проекте:')}\n"
        f"Мы создали удобную и прибыльную экосистему, где ваши активы работают на вас 24/7. Никаких сложных настроек — начинайте зарабатывать криптовалюту в пару кликов!\n\n"
        f"💰 {hbold('Как вы будете зарабатывать?')}\n"
        f"• 📈 {hbold('Ежедневный доход:')} Получайте стабильные {hbold('5%')} дохода каждый день от суммы вашего депозита.\n"
        f"• 🤝 {hbold('Реферальная программа:')} Приглашайте друзей по своей ссылке и получайте {hbold('5%')} от суммы их депозита! Больше друзей — больше заработка!\n"
        f"• ⚡ {hbold('Быстро и надежно:')} Моментальные начисления и безопасный вывод средств на ваш кошелек.\n\n"
        f"👇 Нажмите на кнопку ниже, чтобы запустить приложение и начать майнинг!"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Play Mining",
                    web_app=WebAppInfo(url="https://ton-cosmos-miner.lovable.app/")
                )
            ],
            [
                InlineKeyboardButton(text="📢 Наш канал", url="https://t.me/TonSpaceMine"),
                InlineKeyboardButton(text="💬 Наш чат", url="https://t.me/TonSpaceMineChat")
            ]
        ]
    )

    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")

# Функсияи Рассылка бо дастгирии Акс ва Видео (Танҳо барои @Axmadov2025)
@dp.message(Command("send"))
async def broadcast_message(message: types.Message) -> None:
    if message.from_user.username != "Axmadov2025":
        await message.answer("❌ Шумо ҳуқуқи админ надоред!")
        return

    text_to_send = ""
    if message.text:
        text_to_send = message.text.replace("/send", "").strip()
    elif message.caption:
        text_to_send = message.caption.replace("/send", "").strip()

    has_media = bool(message.photo or message.video)

    if not text_to_send and not has_media:
        await message.answer("✍️ Илтимос, матн ё аксро бо фармони /send равон кунед.\n\nНамуна: `/send Салом ба ҳама!`", parse_mode="Markdown")
        return

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    
    success_count = 0
    await message.answer("⏳ Рассылка оғоз шуд, лутфан интизор шавед...")

    for (u_id,) in users:
        try:
            if message.photo:
                await message.bot.send_photo(chat_id=u_id, photo=message.photo[-1].file_id, caption=text_to_send, parse_mode="HTML")
            elif message.video:
                await message.bot.send_video(chat_id=u_id, video=message.video.file_id, caption=text_to_send, parse_mode="HTML")
            else:
                await message.bot.send_message(chat_id=u_id, text=text_to_send, parse_mode="HTML")
            
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass 

    await message.answer(f"✅ Рассылка ба анҷом расид!\nПаём ба {success_count} нафар фиристода шуд.")

async def main() -> None:
    # Оғоз кардани сервери "Бедоркунак" (Flask)
    keep_alive()
    
    # Оғоз кардани бот
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
