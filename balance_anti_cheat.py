from connect_bd import connect_data_b


async def check_and_update_rank(user_id, new_rank, points, message):
    connection, cursor = connect_data_b()

    try:
        cursor.execute('SELECT * FROM reputation WHERE user_id = %s', (user_id,))
        user_data = cursor.fetchone()

        if not user_data:
            cursor.execute('INSERT INTO reputation (user_id, money, ranks) VALUES (%s, %s, %s)',
                           (user_id, points, new_rank))
            return True

        ranks = user_data[4].split('|') if user_data[4] else []
        if new_rank not in ranks:
            new_ranks = '|'.join(ranks + [new_rank])
            new_reputation = user_data[5] + points

            cursor.execute('UPDATE reputation SET money = %s, ranks = %s WHERE user_id = %s',
                           (new_reputation, new_ranks, user_id))

            money_difference = new_reputation - user_data[5]

            cursor.execute('UPDATE users SET money=money + %s WHERE user_id = %s', (money_difference, user_id,))

            cursor.execute('SELECT user_id FROM users WHERE user_id = %s', (user_id,))
            if cursor.fetchone() is None:
                await message.answer(f"❗️KRAFT coins не начислены, так как пользователь не найден в магазине❗\n"
                                     f"Примите правила магазина и обратитесь к администрации!")
            return True
        else:
            return False
    finally:
        cursor.close()
        connection.close()

