from aiogram import Dispatcher, types

from core.data_base.base import check_user_in_users, registration_user
from core.keyboards.inline import rasp_menu, generate_keyboard_sub_rasp, generate_keyboard_getting_rasp
from core.utils_bot.send_rasp import del_message
from core.utils_bot.text_to_send import rasp_menu_text, settings_rasp_menu_text
from create_bot import bot


async def get_rasp_menu(message: types.CallbackQuery):
    await del_message(message)

    if not check_user_in_users(message.from_user.id):
        registration_user(message.from_user.id)
    await bot.send_message(message.from_user.id, rasp_menu_text, reply_markup=rasp_menu)


async def get_menu_getting_rasp(message: types.CallbackQuery):
    await del_message(message)
    if not check_user_in_users(message.from_user.id):
        registration_user(message.from_user.id)
    await bot.send_message(message.from_user.id, 'Здесь вы можете получить расписание по заданным настройкам',
                           reply_markup=generate_keyboard_getting_rasp(message.from_user.id))


async def get_settings_menu(message: types.CallbackQuery):
    await del_message(message)
    if not check_user_in_users(message.from_user.id):
        registration_user(message.from_user.id)
    await bot.send_message(message.from_user.id, settings_rasp_menu_text,
                           reply_markup=generate_keyboard_sub_rasp(message.from_user.id))


def register__rasp_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_rasp_menu, text='get_rasp_menu')
    dp.register_callback_query_handler(get_settings_menu, text='menu_settings_rasp')
    dp.register_callback_query_handler(get_menu_getting_rasp, text='menu_get_rasp')



