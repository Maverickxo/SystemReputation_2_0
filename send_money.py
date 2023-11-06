import sqlite3
from aiogram import types
import asyncio
from config import *
from money_log import transaction_log

# Подключение к базе данных SQLite
conn = sqlite3.connect(STORE_BD)
cur = conn.cursor()


# функция для получения баланса пользователя
def get_balance(user_id):
    cur = conn.cursor()
    cur.execute("SELECT money FROM users WHERE user_id = ?", (user_id,))

    balance = cur.fetchone()
    cur.close()
    return balance[0] if balance else 0


# функция для добавления монет на баланс пользователя
def add_coins(user_id, coins):
    cur = conn.cursor()
    cur.execute("UPDATE users SET money = money + ? WHERE user_id = ?", (coins, user_id))
    conn.commit()
    cur.close()


# функция для удаления монет с баланса пользователя
def remove_coins(user_id, coins):
    cur = conn.cursor()
    cur.execute("UPDATE users SET money = money - ? WHERE user_id = ?", (coins, user_id))
    conn.commit()
    cur.close()


async def send_coins_to_user(message: types.Message):
    sender_username = message.from_user.mention
    sender_user_id = message.from_user.id
    sender_fullname = message.from_user.full_name
    recip_username = message.reply_to_message.from_user.mention
    recip_user_id = message.reply_to_message.from_user.id
    recipient_fullname = message.reply_to_message.from_user.full_name

    words = message.text.split()
    if len(words) == 1:
        msg = await message.answer("Выберите пользователя и укажите монеты")  #

    else:
        sender_id = message.from_user.id
        cur.execute('SELECT user_id, full_name FROM users WHERE user_id=?', (sender_id,))
        sender = cur.fetchone()
        if sender is None:
            msg = await message.reply('Вы не зарегистрированы в системе')  #
            await asyncio.sleep(MSG_TIMER)
            await msg.delete()
            await message.delete()
            return
        user_id = message.reply_to_message.from_user.id
        cur.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
        user_exists = cur.fetchone()
        user_first_name = message.reply_to_message.from_user.full_name
        if user_exists is None:
            msg = await message.reply(f'{user_first_name} Не найден системе!')  #
            await asyncio.sleep(MSG_TIMER)
            await msg.delete()
            await message.delete()
            return
        command_args = message.text.split()[1:]  # Exclude the command itself
        if len(command_args) == 0:
            msg = await message.reply('Вы не указали количество монет для отправки')
            await asyncio.sleep(MSG_TIMER)
            await msg.delete()
            await message.delete()
            return
        try:
            coins = int(command_args[0])
            if coins < 0:
                raise ValueError('Указано отрицательное количество монет')
        except ValueError:
            msg = await message.reply('Указано неверное количество монет')
            await asyncio.sleep(MSG_TIMER)
            await msg.delete()
            await message.delete()
            return
        sender_balance = get_balance(sender_id)
        if sender_balance < coins:
            msg = await message.reply(f'У вас недостаточно монет!!\nБаланс: {sender_balance}')
            await asyncio.sleep(MSG_TIMER)
            await msg.delete()
            await message.delete()
            return
        add_coins(user_id, coins)
        remove_coins(sender_id, coins)
        msg = await message.reply(f'Вы успешно отправили {coins} KRAFT coins\nпользователю {user_first_name}')

        # TODO: проверка активности при переводе
        await transaction_log(sender_username, sender_user_id, sender_fullname, recip_username, recip_user_id,
                              recipient_fullname, coins, message)

    await asyncio.sleep(MSG_TIMER)
    await msg.delete()
    await message.delete()


async def gopstop_coins_to_user(message: types.Message):
    words = message.text.split()
    if len(words) == 1:
        msg = await message.answer("Выберите пользователя и укажите монеты")
        await message.delete()
        await asyncio.sleep(5)
        await msg.delete()
    else:
        self_user_id = message.from_user.id
        user_id = message.reply_to_message.from_user.id
        cur.execute('SELECT user_id, money FROM users WHERE user_id=?', (user_id,))
        user_data = cur.fetchone()

        if user_data is None:
            user_first_name = message.reply_to_message.from_user.full_name
            msg = await message.reply(f'{user_first_name} не найден в системе!')
            await asyncio.sleep(MSG_TIMER)
            await msg.delete()
            await message.delete()
            return

        user_first_name = message.reply_to_message.from_user.full_name
        user_balance = user_data[1]  # Получаем баланс пользователя

        command_args = message.text.split()[1:]  # Exclude the command itself
        if len(command_args) == 0:
            msg = await message.reply('Вы не указали количество монет для списания')
            await asyncio.sleep(MSG_TIMER)
            await msg.delete()
            await message.delete()
            return

        try:
            coins_to_remove = int(command_args[0])
            if coins_to_remove <= 0:
                raise ValueError('Указано некорректное количество монет')

            coins_to_remove = min(coins_to_remove, user_balance)  # Не списываем больше, чем есть на балансе
        except ValueError:
            msg = await message.reply('Указано неверное количество монет')
            await asyncio.sleep(MSG_TIMER)
            await msg.delete()
            await message.delete()
            return

        new_balance = user_balance - coins_to_remove
        remove_coins(user_id, coins_to_remove)
        add_coins(self_user_id, coins_to_remove)
        if new_balance == 0:
            TEXT_REPLY = f'Гопстоп, {user_first_name}! Ты в нуле!'
        else:
            TEXT_REPLY = f'Вы успешно списали {coins_to_remove} KRAFT coins у пользователя {user_first_name}'

        msg = await message.answer(TEXT_REPLY)

        await asyncio.sleep(MSG_TIMER)
        await msg.delete()
        await message.delete()
