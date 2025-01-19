import asyncio
from os import mkdir
from os.path import exists

from aiogram import executor

from config import path_news_files, path_RF, path_temp
from core.data_base.base import start_db, update_groups_info, update_cabinet_name, backup_database
from core.handlers.all_rasp_handlers import register_all_rasp_handlers
from core.handlers.cabinet_handler import register_cabinet_handlers
from core.handlers.getting_rasp_handlers import register__rasp_handlers
from core.handlers.general_handler import register_general_handlers
from core.handlers.student_rasp_handlers import register_student_rasp_handlers
from core.handlers.subscribe_handlers import register_subscribe_handlers
from core.handlers.teacher_rasp_handlers import register_teacher_rasp_handlers
from create_bot import dp
from check_rasp import sending_messages


async def on_startup(_):
    """Функция запускается при старте проекта"""

    # создаем директории
    for dir_file in (path_RF, path_news_files, f'{path_news_files}/photo', path_temp):
        if not exists(dir_file):
            mkdir(dir_file)

    start_db()  # запуск БД
    update_groups_info()  # обновляем информацию о группах
    update_cabinet_name()  # обновляем информацию о кабинетах

    print('BOT ONLINE')
    asyncio.create_task(sending_messages())  # запускаем обработчик расписания
    asyncio.create_task(backup_database())  # запускаем создание бекапов БД


if __name__ == "__main__":
    """Регистрируем хендлеры и заупскаем работу бота"""
    register_general_handlers(dp)
    register__rasp_handlers(dp)
    register_subscribe_handlers(dp)
    register_cabinet_handlers(dp)

    register_student_rasp_handlers(dp)
    register_all_rasp_handlers(dp)
    register_teacher_rasp_handlers(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)



