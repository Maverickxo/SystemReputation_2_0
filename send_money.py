from aiogram import types
import asyncio
from money_log import transaction_log

from clear_msg import process_reply_msg_delete, process_answer_msg_delete

from connect_bd import connect_data_b


# функция для получения баланса пользователя
def get_balance(user_id):
    connection, cursor = connect_data_b()
    cursor.execute("SELECT money FROM users WHERE user_id = %s", (user_id,))
    balance = cursor.fetchone()
    cursor.close()
    connection.close()
    return balance[0] if balance else 0


# функция для добавления монет на баланс пользователя
def add_coins(user_id, coins):
    connection, cursor = connect_data_b()
    cursor.execute("UPDATE users SET money = money + %s WHERE user_id = %s", (coins, user_id,))
    cursor.close()
    connection.close()


# функция для удаления монет с баланса пользователя
def remove_coins(user_id, coins):
    connection, cursor = connect_data_b()
    cursor.execute("UPDATE users SET money = money - %s WHERE user_id = %s", (coins, user_id,))
    cursor.close()
    connection.close()


async def send_coins_to_user(message: types.Message, money_arg, comments_arg):
    connection, cursor = connect_data_b()
    try:
        sender_username = message.from_user.mention
        sender_user_id = message.from_user.id
        sender_fullname = message.from_user.full_name
        recip_username = message.reply_to_message.from_user.mention
        recip_user_id = message.reply_to_message.from_user.id
        recipient_fullname = message.reply_to_message.from_user.full_name
    except Exception:
        await process_answer_msg_delete(message, "Выберите пользователя и укажите монеты", 5)

    else:
        sender_id = message.from_user.id
        cursor.execute('SELECT user_id, full_name FROM users WHERE user_id = %s', (sender_id,))
        sender = cursor.fetchone()
        if sender is None:
            await process_reply_msg_delete(message, 'Вы не зарегистрированы в системе', 10)  #
            return
        user_id = message.reply_to_message.from_user.id
        cursor.execute('SELECT user_id FROM users WHERE user_id = %s', (user_id,))
        user_exists = cursor.fetchone()
        user_first_name = message.reply_to_message.from_user.full_name
        if user_exists is None:
            await process_reply_msg_delete(message, f'{user_first_name} Не найден системе!')  #
            return
        try:
            coins = int(money_arg)
            if coins < 0:
                raise ValueError('Указано отрицательное количество монет')
        except ValueError:
            await process_reply_msg_delete(message, 'Указано неверное количество монет', 5)
            return
        sender_balance = get_balance(sender_id)
        if sender_balance < coins:
            await process_reply_msg_delete(message, f'У вас недостаточно монет!!\nБаланс: {sender_balance}', 5)
            return
        add_coins(user_id, coins)
        remove_coins(sender_id, coins)
        await process_reply_msg_delete(message,
                                       f'Вы успешно отправили {coins} KRAFT coins\n'
                                       f'Пользователю: {user_first_name}\n'
                                       f'Причина: {comments_arg}', 20)

        # TODO: проверка активности при переводе
        await transaction_log(sender_username, sender_user_id, sender_fullname, recip_username, recip_user_id,
                              recipient_fullname, coins, message,comments_arg)
    cursor.close()
    connection.close()


async def gopstop_coins_to_user(message: types.Message):
    await message.delete()
    connection, cursor = connect_data_b()

    words = message.text.split()
    if len(words) == 1:
        msg = await message.answer("Выберите пользователя и укажите монеты")
        await message.delete()
        await asyncio.sleep(5)
        await msg.delete()
    else:
        self_user_id = message.from_user.id
        user_id = message.reply_to_message.from_user.id
        cursor.execute('SELECT user_id, money FROM users WHERE user_id = %s', (user_id,))
        user_data = cursor.fetchone()

        if user_data is None:
            user_first_name = message.reply_to_message.from_user.full_name
            await process_reply_msg_delete(message, f'{user_first_name} не найден в системе!', 5)
            return

        user_first_name = message.reply_to_message.from_user.full_name
        user_balance = user_data[1]  # Получаем баланс пользователя

        command_args = message.text.split()[1:]  # Exclude the command itself
        if len(command_args) == 0:
            await process_reply_msg_delete(message, 'Вы не указали количество монет для списания', 5)

            return

        try:
            coins_to_remove = int(command_args[0])
            if coins_to_remove <= 0:
                raise ValueError('Указано некорректное количество монет')

            coins_to_remove = min(coins_to_remove, user_balance)  # Не списываем больше, чем есть на балансе
        except ValueError:
            await process_reply_msg_delete(message, 'Указано неверное количество монет', 5)

            return

        new_balance = user_balance - coins_to_remove
        remove_coins(user_id, coins_to_remove)
        add_coins(self_user_id, coins_to_remove)
        if new_balance == 0:
            TEXT_REPLY = f'Гопстоп, {user_first_name}! Ты в нуле!'
        else:
            TEXT_REPLY = f'Вы успешно списали {coins_to_remove} KRAFT coins у пользователя {user_first_name}'

        await process_answer_msg_delete(message, TEXT_REPLY, 10)
