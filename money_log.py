import datetime
import json
import re
import os
from aiogram import types

time_threshold_minutes = 5
max_transactions = 3


def clean_user_name(filename):
    return re.sub(r'[\/:*?"<>|]', '_', filename)


def check_activity(recipient_username):
    current_time = datetime.datetime.now()
    log_directory = f'log_money/{recipient_username}'
    if not os.path.exists(log_directory):
        return False

    log_files = os.listdir(log_directory)
    log_files.sort()
    transaction_count = 0
    for log_file in log_files:
        log_path = os.path.join(log_directory, log_file)
        with open(log_path, 'r') as file:
            log_data = json.load(file)
            log_time = datetime.datetime.strptime(log_data['Дата'] + ' ' + log_data['Время'], "%Y-%m-%d %H:%M:%S")
            time_difference = current_time - log_time
            if time_difference.total_seconds() <= time_threshold_minutes * 60:
                transaction_count += 1
                if transaction_count >= max_transactions:
                    return True
    return False


async def transaction_log(sender_username, sender_user_id, sender_fullname, recip_username, recip_user_id,
                          recipient_fullname, amount, message: types.Message):
    current_datetime = datetime.datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d")
    time_log_name = current_datetime.strftime("%H-%M-%S")
    recipient_fullname_cl = clean_user_name(recipient_fullname)

    recipient_directory = f'log_money/{recipient_fullname_cl}'

    if not os.path.exists(recipient_directory):
        os.makedirs(recipient_directory)

    log_entry = {
        "Дата": formatted_date,
        "Время": current_datetime.strftime("%H:%M:%S"),
        "От кого": {
            "Username": sender_username,
            "UserID": sender_user_id,
            "Полное имя": sender_fullname
        },
        "Кому": {
            "Username": recip_username,
            "UserID": recip_user_id,
            "Полное имя": recipient_fullname
        },
        "Сколько монет": amount
    }

    with open(f'{recipient_directory}/{formatted_date} ({time_log_name})_transaction_log.json',
              'a') as log_file:
        json.dump(log_entry, log_file, ensure_ascii=False, indent=4)

    if check_activity(recipient_fullname):
        print("Требуется проверка на подозрительную активность.")

        await message.answer(f"Требуется проверка на подозрительную активность.\nПользователь: {recipient_fullname}")
    else:
        print("Нет подозрительной активности.")
