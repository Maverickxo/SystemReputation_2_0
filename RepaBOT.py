from aiogram import Bot, Dispatcher, executor
import asyncio as messagedelete
import logging
from balance_anti_cheat import check_and_update_rank

from send_money import send_coins_to_user, gopstop_coins_to_user

import asyncio
from check_access import *
from config import *
from keywords_data import *
from status_bot import on_startup

from connect_bd import connect_data_b

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)

dp = Dispatcher(bot)

RANKS = {
    'Новичок': (0, 1),
    'Бикини': (1, 10),
    'Щегол': (10, 20),
    'Смычек': (20, 30),
    'Турист': (30, 50),
    'Любитель фармы': (50, 100),
    'Билдер': (100, 200),
    'Машина': (200, 250),
    'Животное': (250, 300),
    'Терминатор': (300, 350),
    'mr.Олимпия': (350, 400),
    'Хищник': (400, 450),
    'Кто ты тварь ?': (450, 500),
    'Эксперт': (500, float('inf'))
}


def get_rank(reputation):
    for rank, (min_rep, max_rep) in RANKS.items():
        if min_rep <= reputation < max_rep:
            return rank
    return 'Днище Бля'


# Команда для просмотра репутации участника на основе ключевых слов
@dp.message_handler(
    lambda message: any(keyword in message.text.lower() for keyword in ['рейтинг', 'репа', 'репутация']))
async def get_reputation(message: types.Message):
    connection, cursor = connect_data_b()

    words = message.text.split()
    if len(words) == 1:
        user_id = message.from_user.id
        user_name = message.from_user.full_name

        cursor.execute('SELECT reputation FROM reputation WHERE user_id = %s', (user_id,))
        row = cursor.fetchone()
        if row is None:
            cursor.execute('INSERT INTO reputation (user_id, reputation, user_name) VALUES (%s, %s, %s)',
                           (user_id, 0, user_name))

            sent_message = await message.reply(f'Поздравляю с регистрацией!'
                                               f'\nВаша репутация: 0 '
                                               f'\nВаше звание: Новичок'
                                               f'\nПри повышении звания вам будут начислены KRAFT coins . Удачи!')
            await messagedelete.sleep(10)
            try:
                await sent_message.delete()
            except Exception as e:
                print(e)
        else:
            reputation = row[0]
            rank = get_rank(reputation)
            reply_text = f'Ваша репутация:'f' {reputation} \nВаше звание: {rank}.'
            sent_message = await message.reply(reply_text)
            await messagedelete.sleep(10)
            try:
                await sent_message.delete()
            except Exception as e:
                print(e)

    cursor.close()
    connection.close()


# Команда для увеличения репутации участника на основе ключевых слов
@dp.message_handler(
    lambda message: any(
        keyword in message.text.lower() for keyword in ['спасибо', 'круто', 'спс', 'благодарю', '+', '👍']))
async def increase_reputation(message: types.Message):
    connection, cursor = connect_data_b()

    words = message.text.split()
    if len(words) == 1:
        if message.reply_to_message is None:
            sent_message = await message.reply("Пожалуйста, отправьте ваше сообщение в ответ на другое сообщение.")
            await messagedelete.sleep(10)
            try:
                await sent_message.delete()
            except Exception as e:
                print(e)
            return

        sender_id = message.from_user.id
        recipient_id = message.reply_to_message.from_user.id

        if sender_id == recipient_id:
            sent_message = await message.reply("Вы не можете увеличить свою собственную репутацию.")
            await messagedelete.sleep(10)
            try:
                await sent_message.delete()
            except Exception as e:
                print(e)
            return

        change_value = 1
        cursor.execute('SELECT reputation FROM reputation WHERE user_id = %s', (recipient_id,))
        row = cursor.fetchone()
        user_name = message.reply_to_message.from_user.full_name
        user_id = message.reply_to_message.from_user.id
        if row is None:
            reply_text = f'Пользователь {user_name} не найден в базе данных репутации'
            sent_message = await message.reply(reply_text)

            await messagedelete.sleep(10)
            try:
                await sent_message.delete()
            except Exception as e:
                print(e)
            return
        else:
            reputation = row[0] + change_value
            cursor.execute('UPDATE reputation SET reputation = %s WHERE user_id = %s', (reputation, recipient_id))

            points_for_rank = 500

            rank = get_rank(reputation)
            if await check_and_update_rank(user_id, rank, points_for_rank, message):
                print(f"Баллы успешно начислены за звание: {rank}")
            else:
                print(f"Баллы уже были начислены за это звание: {rank}")

            rank = get_rank(reputation)
            reply_text = (
                f'Репутация пользователя {message.reply_to_message.from_user.first_name} увеличена на {abs(change_value)}.'
                f'\nТекущая репутация: {reputation} \nВаше звание: {rank}.')
            sent_message = await message.reply(reply_text)
            await messagedelete.sleep(10)
            try:
                await sent_message.delete()
            except Exception as e:
                print(e)
    cursor.close()
    connection.close()


# Команда для уменьшения репутации участника на основе ключевых слов
@dp.message_handler(lambda message: any(keyword in message.text.lower() for keyword in ['👎']))
async def decrease_reputation(message: types.Message):
    connection, cursor = connect_data_b()

    words = message.text.split()
    if len(words) == 1:
        if message.reply_to_message is None:
            sent_message = await message.reply("Пожалуйста, отправьте ваше сообщение в ответ на другое сообщение.")
            await messagedelete.sleep(10)
            try:
                await sent_message.delete()
            except Exception as e:
                print(e)
            return

        if message.reply_to_message.from_user.id == message.from_user.id:
            sent_message = await message.reply("Нельзя уменьшать свою собственную репутацию.")
            await messagedelete.sleep(10)
            try:
                await sent_message.delete()
            except Exception as e:
                print(e)
            return

        user_id = message.reply_to_message.from_user.id
        change_value = -1
        cursor.execute('SELECT reputation FROM reputation WHERE user_id = %s', (user_id,))
        row = cursor.fetchone()

        user_name = message.reply_to_message.from_user.full_name
        if row is None:
            reply_text = f'Пользователь {user_name} не найден в базе данных репутации'
            sent_message = await message.reply(reply_text)

            await messagedelete.sleep(10)
            try:
                await sent_message.delete()
            except Exception as e:
                print(e)
            return
        else:
            reputation = row[0] + change_value
            cursor.execute('UPDATE reputation SET reputation = %s WHERE user_id = %s', (reputation, user_id))
            rank = get_rank(reputation)

            reply_text = (f'Репутация пользователя {message.reply_to_message.from_user.full_name}\n'
                          f'уменьшена на {abs(change_value)}.\n'
                          f'Текущая репутация: {reputation} \nВаше звание: {rank}.')

            sent_message = await message.reply(reply_text)
            await messagedelete.sleep(10)
            try:
                await sent_message.delete()
            except Exception as e:
                print(e)
    cursor.close()
    connection.close()


# Команда для запроса общего рейтинга
@dp.message_handler(commands=['rating'])
async def get_rating(message: types.Message):  # TODO готово
    await message.delete()
    connection, cursor = connect_data_b()
    try:
        top_count = int(message.text.split()[1])
    except (IndexError, ValueError):
        top_count = 100
    cursor.execute(
        'SELECT user_id, reputation, user_name FROM reputation WHERE reputation >0 ORDER BY reputation DESC LIMIT %s',
        (top_count,))
    rows = cursor.fetchall()

    if not rows:
        sent_message = await message.reply('Нет данных о репутации пользователей')
        await messagedelete.sleep(20)
        try:
            await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
        except Exception as e:
            print(e)
        return

    sent_messages = []
    chunk_size = 30
    rows_per_message = [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]

    for chunk_rows in rows_per_message:
        rating_text = f'Топ-{top_count} пользователей:\n'
        for i, row in enumerate(chunk_rows):
            user_id, reputation, user_name = row
            rank = get_rank(reputation)
            rating_text += f'{i + 1}. {user_name} Репутация: {reputation} Звание: {rank}\n'

        sent_message = await message.answer(rating_text)
        sent_messages.append(sent_message)

    await asyncio.sleep(20)
    for sent_message in sent_messages:
        try:
            await sent_message.delete()
        except Exception as e:
            print(e)

    cursor.close()
    connection.close()


# Команда для отправки от имени бота в чат
@dp.message_handler(commands=['speak_chat'])
@auth
@check_type_chat()
async def send_to_chat(message: types.Message):
    text = message.text.replace("/speak_chat ", "")
    await bot.send_message(chat_id=-1001205041376, text=text)


@dp.message_handler(commands=['send'])
async def send_coins_to(message: types.Message):
    command_args = message.get_args()
    if len(command_args) == 0:
        await message.answer("Вы не указали количество монет"
                             " и причину - `/send 1 причина`", parse_mode='markdown')
    else:
        args = command_args.split(maxsplit=1)
        money_arg = args[0]
        if len(args) > 1:
            comments_arg = args[1]
        else:
            comments_arg = "Не указана"
        await send_coins_to_user(message, money_arg, comments_arg)


@dp.message_handler(commands=['gopstop'])
@auth
async def gopstop_to_money(message: types.Message):
    await gopstop_coins_to_user(message)


@dp.message_handler(commands=['rank_system'])
@auth
async def rank_system_handler(message: types.Message):
    await message.delete()
    await message.answer(Rank_System, parse_mode='markdown')


if __name__ == '__main__':
    # create_database()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
