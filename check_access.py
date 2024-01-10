from aiogram import types


def auth(func):
    allowed_ids = [5869013585, 5967935518, 1444325514, 5633493512]

    async def wrapper(message):
        if message['from']['id'] not in allowed_ids:
            return await message.reply("Доступ запрещен", reply=False)
        return await func(message)

    return wrapper


def check_type_chat():
    def decorator(func):
        async def wrapper(message: types.Message):
            if message.chat.type != types.ChatType.PRIVATE:
                pass
                return
            return await func(message)

        return wrapper

    return decorator
