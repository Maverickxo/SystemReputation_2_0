from config import TOKEN
from aiogram import Bot
from date_time_online import online_date_time
bot = Bot(token=TOKEN)


async def on_startup(dispatcher):  # Отправка сообщения при запуске бота

    moscow_time = online_date_time()
    await bot.send_message(chat_id=5869013585, text=f"Бот запущен! {moscow_time}MSK")
