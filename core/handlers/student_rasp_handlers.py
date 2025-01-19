import os
import traceback

from aiogram import Dispatcher, types

from config import name_statistic_func, path_RF, name_statistic_button
from core.data_base.base import add_data_statistic, get_group, check_user_in_users, registration_user
from core.keyboards.inline import rasp_menu
from core.keyboards.simple import generate_groups_keyboard, generate_days_keyboard, level_student
from core.utils_bot.classes_state import GetStatusGroup, GetDayStudent
from core.utils_bot.rasp_utils import delete_keyboard
from core.utils_bot.send_rasp import send_rasp_student, del_message
from create_bot import bot


async def get_student_rasp_button(message: types.CallbackQuery):
    if not check_user_in_users(message.from_user.id):
        registration_user(message.from_user.id)

    await del_message(message)
    await GetDayStudent.day.set()
    await bot.send_message(message.from_user.id, 'На какой день вам нужно расписание?',
                           reply_markup=generate_days_keyboard())


async def get_day_rasp_button(message: types.Message, state):
    if message.text not in os.listdir(path_RF):
        await bot.send_message(message.from_user.id,
                               'Такого дня не существует, попробуйте снова!',
                               reply_markup=generate_days_keyboard())
        return
    try:
        days = (message.text, )
        await send_rasp_student(message.from_user.id, days, mailing=False)
        add_data_statistic(name_statistic_button, 'student')
    except:
        add_data_statistic(name_statistic_button, 'student_errors')
        print(traceback.format_exc())

    await state.finish()
    await delete_keyboard(message)


async def get_campus_rasp_one(message: types.Message):
    if not check_user_in_users(message.from_user.id):
        registration_user(message.from_user.id)

    await GetStatusGroup.day.set()
    await bot.send_message(message.from_user.id, 'На какой день вам нужно расписание?', reply_markup=generate_days_keyboard())


async def get_day_rasp_one(message: types.Message, state):
    if message.text not in os.listdir(path_RF):
        await bot.send_message(message.from_user.id,
                               'Такого дня не существует, попробуйте снова!',
                               reply_markup=generate_days_keyboard())
        return

    async with state.proxy() as data:
        data['day'] = message.text

    await GetStatusGroup.campus.set()
    await bot.send_message(message.from_user.id, 'Выберите курс группы', reply_markup=level_student)


async def get_group_name_rasp_one(message: types.Message, state):
    if message.text not in ['1', '2', '3', '4']:
        await bot.send_message(message.from_user.id, 'Такого корпуса не существует, попробуйте снова!')
        return

    async with state.proxy() as data:
        data['campus'] = int(message.text)

    keyboard = generate_groups_keyboard(get_group(message.text))

    await bot.send_message(message.from_user.id, 'Выберите группу на клавиатуре', reply_markup=keyboard)
    await GetStatusGroup.group_name.set()


async def get_group_rasp_one(message: types.Message, state):
    group_name = message.text.replace('/get_rs', '')
    if len(message.text.strip().lower().replace(' ', '').replace('.', '')) < 5:
        await bot.send_message(message.from_user.id, 'Неккоректно введено имя группы', reply_markup=rasp_menu)
        return

    try:
        async with state.proxy() as data:
            days = (data['day'], )

        await send_rasp_student(message.from_user.id, days, mailing=False, command=True, group_student=group_name)

        add_data_statistic(name_statistic_func, 'student')
    except:
        add_data_statistic(name_statistic_func, 'student_errors')
        print(traceback.format_exc())

    await state.finish()
    await delete_keyboard(message)


def register_student_rasp_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_student_rasp_button, text='get_rasp_student', state=None)
    dp.register_message_handler(get_day_rasp_button, state=GetDayStudent.day)

    dp.register_message_handler(get_campus_rasp_one, commands=['get_rs'], state=None)
    dp.register_message_handler(get_day_rasp_one, state=GetStatusGroup.day)
    dp.register_message_handler(get_group_name_rasp_one, state=GetStatusGroup.campus)
    dp.register_message_handler(get_group_rasp_one, state=GetStatusGroup.group_name)
