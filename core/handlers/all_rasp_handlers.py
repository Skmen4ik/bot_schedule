import os
import traceback

from aiogram import Dispatcher, types

from config import name_statistic_button, path_RF
from core.data_base.base import add_data_statistic, check_user_in_users, registration_user
from core.keyboards.simple import generate_days_keyboard
from core.utils_bot.classes_state import GetDayAllRasp
from core.utils_bot.rasp_utils import delete_keyboard
from core.utils_bot.send_rasp import send_all_rasp
from create_bot import bot


async def get_full_rasp_once(message: types.CallbackQuery):
    if not check_user_in_users(message.from_user.id):
        registration_user(message.from_user.id)

    await GetDayAllRasp.day.set()
    await bot.send_message(message.from_user.id, 'На какой день вам нужно расписание?',
                           reply_markup=generate_days_keyboard())


async def get_full_rasp(message: types.Message, state):
    if message.text not in os.listdir(path_RF):
        await bot.send_message(message.from_user.id,
                               'Такого дня не существует, попробуйте снова!',
                               reply_markup=generate_days_keyboard())
        return

    try:
        days = (message.text, )
        await send_all_rasp(message.from_user.id, days, mailing=False, button_start=True)
        add_data_statistic(name_statistic_button, 'all_rasp')
    except:
        add_data_statistic(name_statistic_button, 'all_rasp_errors')
        print(traceback.format_exc())

    await state.finish()
    await delete_keyboard(message)


def register_all_rasp_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_full_rasp_once, text='get_all_rasp', state=None)
    dp.register_message_handler(get_full_rasp, state=GetDayAllRasp.day)

    dp.register_message_handler(get_full_rasp_once, commands=['fullrasp'], state=None)
