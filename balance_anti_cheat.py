import sqlite3
from config import *
from aiogram import types


async def check_and_update_rank(user_id, new_rank, points, message):
    conn = sqlite3.connect(REPA_BD)
    cursor = conn.cursor()
    conn1 = sqlite3.connect(STORE_BD)
    cursor1 = conn1.cursor()
    try:
        cursor.execute('BEGIN')
        cursor.execute('SELECT * FROM reputation WHERE user_id=?', (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            cursor.execute('INSERT INTO reputation (user_id, money, ranks) VALUES (?, ?, ?)',
                           (user_id, points, new_rank))
            return True
        ranks = user_data[3].split('|') if user_data[3] else []
        if new_rank not in ranks:
            new_ranks = '|'.join(ranks + [new_rank])
            new_reputation = user_data[4] + points
            cursor.execute('UPDATE reputation SET money=?, ranks=? WHERE user_id=?',
                           (new_reputation, new_ranks, user_id))
            cursor.execute('COMMIT')
            money_difference = new_reputation - user_data[4]

            cursor1.execute('UPDATE users SET money=money + ? WHERE user_id=?',
                            (money_difference, user_id))

            cursor1.execute('COMMIT')

            cursor1.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
            if cursor1.fetchone() is None:
                await message.answer(f"❗️KRAFT coins не начислены, так как пользователь не найден в магазине❗\n"
                                     f"Примите правила магазина и обратитесь к администрации!")
            return True
        else:
            return False
    except:
        cursor.execute('ROLLBACK')
        raise
    finally:
        conn.close()
        conn1.close()

#
# def user_exists(user_id):
#     conn = sqlite3.connect(STORE_BD)
#     cursor = conn.cursor()
#
#     try:
#         cursor.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
#         result = cursor.fetchone()
#         return result is not None
#     finally:
#         conn.close()
#
#     if user_exists(user_id):
#         pass
#     else:
#         pass

# import sqlite3
#
#
# def connect_to_database(database_name):
#     return sqlite3.connect(database_name)
#
#
# def update_reputation(conn, user_id, new_rank, points):
#     cursor = conn.cursor()
#     try:
#         cursor.execute('BEGIN')
#         cursor.execute('SELECT * FROM reputation WHERE user_id=?', (user_id,))
#         user_data = cursor.fetchone()
#         if not user_data:
#             cursor.execute('INSERT INTO reputation (user_id, money, ranks) VALUES (?, ?, ?)',
#                            (user_id, points, new_rank))
#             return True
#         ranks = user_data[3].split('|') if user_data[3] else []
#         if new_rank not in ranks:
#             new_ranks = '|'.join(ranks + [new_rank])
#             new_reputation = user_data[4] + points
#             cursor.execute('UPDATE reputation SET money=?, ranks=? WHERE user_id=?',
#                            (new_reputation, new_ranks, user_id))
#             cursor.execute('COMMIT')
#             return new_reputation
#         else:
#             return False
#     except:
#         cursor.execute('ROLLBACK')
#         raise
#
#
# def update_users_money(conn, user_id, money_difference):
#     cursor = conn.cursor()
#     cursor.execute('UPDATE users SET money=money + ? WHERE user_id=?',
#                    (money_difference, user_id))
#     cursor.execute('COMMIT')
#
#
# def check_and_update_rank(user_id, new_rank, points):
#     reputation_conn = connect_to_database('reputation.db')
#     users_conn = connect_to_database('C:/PYTHON_PJ/KRAFT_STROE_3_0/ShopDB.db')
#
#     try:
#         new_reputation = update_reputation(reputation_conn, user_id, new_rank, points)
#
#         if new_reputation is not False:
#             money_difference = new_reputation - points
#             update_users_money(users_conn, user_id, money_difference)
#             return True
#         else:
#             return False
#     finally:
#         reputation_conn.close()
#         users_conn.close()
