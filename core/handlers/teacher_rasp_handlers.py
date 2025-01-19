import os
import traceback
from shutil import rmtree as rmtree_rmtree

from aiogram import Dispatcher, types

from config import name_statistic_func, name_statistic_button, path_RF, path_temp
from core.data_base.base import add_data_statistic, get_lastname_teacher, check_user_in_users, registration_user
from core.keyboards.inline import rasp_menu
from core.keyboards.simple import generate_days_keyboard
from core.utils_bot.classes_state import GetDayTeacher, GetDayTeacherOne
from core.utils_bot.rasp_utils import delete_keyboard
from core.utils_bot.send_rasp import send_rasp_teacher
from create_bot import bot


async def get_day_teacher_rasp(message: types.CallbackQuery):
    if not check_user_in_users(message.from_user.id):
        registration_user(message.from_user.id)

    await GetDayTeacher.day.set()
    await bot.send_message(message.from_user.id, 'На какой день вам нужно расписание?',
                           reply_markup=generate_days_keyboard())


async def get_teacher_rasp(message: types.Message, state):
    if message.text not in os.listdir(path_RF):
        await bot.send_message(message.from_user.id,
                               'Такого дня не существует, попробуйте снова!',
                               reply_markup=generate_days_keyboard())
        return

    try:
        days = (message.text, )
        path = f'{path_temp}/{message.from_user.id}_teacher'

        if os.path.exists(path):
            rmtree_rmtree(path)

        os.mkdir(path)
        await send_rasp_teacher(get_lastname_teacher(message.from_user.id),
                                path, message.from_user.id, days, mailing=False)
        rmtree_rmtree(path)
        add_data_statistic(name_statistic_button, 'teacher')
    except:
        add_data_statistic(name_statistic_button, 'teacher_errors')
        print(traceback.format_exc())

    await state.finish()
    await delete_keyboard(message)


async def get_lastname_teacher_rasp_one(message: types.Message, state):
    if not check_user_in_users(message.from_user.id):
        registration_user(message.from_user.id)

    lastname = message.text.replace('/get_rt', '')
    if len(lastname.strip().lower().replace(' ', '').replace('.', '')) < 6:
        await bot.send_message(message.from_user.id, 'Неккоректно введены фамилия и инициалы', reply_markup=rasp_menu)
        return

    async with state.proxy() as data:
        data['lastname'] = lastname

    await GetDayTeacherOne.day.set()
    await bot.send_message(message.from_user.id, 'На какой день вам нужно расписание?',
                           reply_markup=generate_days_keyboard())


async def get_day_teacher_rasp_one(message: types.Message, state):
    if message.text not in os.listdir(path_RF):
        await bot.send_message(message.from_user.id,
                               'Такого дня не существует, попробуйте снова!',
                               reply_markup=generate_days_keyboard())
        return

    async with state.proxy() as data:
        lastname = data['lastname']

    try:
        days = (message.text, )
        lastname = lastname.strip().lower().replace(' ', '').replace('.', '')
        path = f'{path_temp}/{message.from_user.id}'
        os.mkdir(path)
        await send_rasp_teacher(lastname, path, message.from_user.id, days, mailing=False)
        rmtree_rmtree(path)
        add_data_statistic(name_statistic_func, 'teacher')
    except:
        add_data_statistic(name_statistic_func, 'teacher_errors')
        print(traceback.format_exc())

    await state.finish()
    await delete_keyboard(message)


def register_teacher_rasp_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_day_teacher_rasp, text='get_rasp_teacher')
    dp.register_message_handler(get_teacher_rasp, state=GetDayTeacher.day)

    dp.register_message_handler(get_lastname_teacher_rasp_one, commands=['get_rt'], state=None)
    dp.register_message_handler(get_day_teacher_rasp_one, state=GetDayTeacherOne.day)
