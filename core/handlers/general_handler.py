import csv
import os

from aiogram import types, Dispatcher

from config import admins_id, path_statistic_func, path_statistic_button
from core.data_base.base import check_user_in_users, registration_user, get_quantity_users, get_statistic_button, \
    get_statistic_func
from core.keyboards.inline import main_menu, back_main_menu_o, rasp_menu
from core.utils_bot.send_rasp import del_message
from core.utils_bot.text_to_send import rasp_menu_text
from create_bot import bot


async def get_start(message: types.Message):
    """Обрабатывает команду /start и возвращает основную клавиатуру"""
    with open('users', 'a', encoding='utf-8') as file:
        file.write(f'https://t.me/{message.chat.username}, {message.from_user.full_name}, {message.from_user.id}\n')

    if not check_user_in_users(message.from_user.id):
        registration_user(message.from_user.id)
    await bot.send_message(message.from_user.id,
                           f'Привет, {message.from_user.full_name}! Получи расписание ПОЛНОСТЬЮ;)\n\n'
                           f'/developers - узнать разработчиков\n'
                           f'По всем багам, предложениям писать сюда: @skmen4ik'
                           , reply_markup=main_menu)


async def to_main_menu(message: types.CallbackQuery):
    """Возвращает в основное меню. Используется при нажатии inline клавиатуры меню расписания"""
    await del_message(message)
    await bot.send_message(message.from_user.id,
                           f'Привет, {message.from_user.full_name}! Получи расписание ПОЛНОСТЬЮ;)\n\n'
                           f'/developers - узнать разработчиков\n'
                           f'По всем багам, предложениям писать сюда: @skmen4ik',
                           reply_markup=main_menu)


async def print_developers(message: types.Message):
    """Выводит список разработчиков проекта. Самая важная функция, НЕ ТРОГАТЬ БЛЕАТ"""
    await bot.send_message(message.from_user.id, 'Повелители своих судеб, мегауспешные люди:\n\n'
                                                 '@skmen4ik - величайший логист&ботовод👑\n'
                                                 '@Deley00 - сержант графоний🎩\n\n'
                                                 '@osinagm - бОтовый сомелье🧐\n'
                                                 '@hoperbanif - бОтовый сомелье🧐', reply_markup=back_main_menu_o)


async def print_statistic(message: types.Message):
    """Обрабатывает приватную команду /stat и выводит статистику по пользователям.
    Работает только для админов, которые указаны в переменной admins_id из файла config.py"""
    text = ('Всего: {}.\n\nПреподаватели: {}\n'
            'Студенты: {}\nПолное расписание: {}\n'
            'Без подписки: {}\n').format(*get_quantity_users())

    list_statistic_button = get_statistic_button()
    with open(path_statistic_button, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow(
            ('all_rasp', 'all_rasp_error', 'teacher', 'teacher_error', 'student', 'student_error', 'date_start'))
        spamwriter.writerows(list_statistic_button)

    list_statistic_func = get_statistic_func()
    with open(path_statistic_func, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow(
            ('all_rasp', 'all_rasp_error', 'teacher', 'teacher_error', 'student', 'student_error', 'date_start', 'cabinets', 'cabinets_errors'))
        spamwriter.writerows(list_statistic_func)

    await bot.send_message(message.from_user.id, text)
    await bot.send_document(message.from_user.id, document=types.InputFile(path_statistic_button))
    await bot.send_document(message.from_user.id, document=types.InputFile(path_statistic_func))

    for file in (path_statistic_button, path_statistic_func):
        os.remove(file)


async def get_menu_rasp(message: types.Message):
    """Обработка команды /menu. Возвращает меню расписания пользователю."""
    if not check_user_in_users(message.from_user.id):
        registration_user(message.from_user.id)

    await bot.send_message(message.from_user.id, rasp_menu_text, reply_markup=rasp_menu)


def register_general_handlers(dp: Dispatcher):
    dp.register_message_handler(get_start, commands=['start'])
    dp.register_message_handler(get_menu_rasp, commands=['menu'])
    dp.register_message_handler(print_developers, commands=['developers'])
    dp.register_callback_query_handler(to_main_menu, text='to_main_menu')
    dp.register_message_handler(print_statistic, lambda message: message.from_user.id in admins_id, commands=['stat'])
