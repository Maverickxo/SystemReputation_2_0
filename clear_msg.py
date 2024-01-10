import asyncio
from aiogram import Bot, types
from config import TOKEN

bot = Bot(token=TOKEN)


async def mesg_del_time(message: types.Message, delay: int):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except:
        print("Сообщение уже было удалено!")


async def process_answer_msg_delete(message, text, delay):
    answer = await message.answer(text, parse_mode='markdown')
    if answer is not None:
        _ = asyncio.create_task(mesg_del_time(answer, delay))


async def process_reply_msg_delete(message, text, delay):
    reply_msg = await message.reply(text, parse_mode='markdown')
    if reply_msg is not None:
        _ = asyncio.create_task(mesg_del_time(reply_msg, delay))
