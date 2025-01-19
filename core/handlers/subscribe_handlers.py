from aiogram import types, Dispatcher
from core.data_base.base import subscribe_to_all_rasp_bd, subscribe_to_teacher_bd, subscribe_to_student_bd, \
    unsubscribe_to_all_rasp_bd, unsubscribe_to_teacher_bd, unsubscribe_to_student_bd, insert_data_teacher, \
    delete_teacher, get_group, check_group_name, insert_data_student, delete_student
from core.keyboards.inline import generate_keyboard_sub_rasp
from core.keyboards.simple import level_student, generate_groups_keyboard
from core.utils_bot.classes_state import RegistrationRasp
from core.utils_bot.send_rasp import del_message
from core.utils_bot.text_to_send import settings_rasp_menu_text

from create_bot import bot


async def subscribe_to_all_rasp(message: types.CallbackQuery):
    await del_message(message)

    subscribe_to_all_rasp_bd(message.from_user.id)
    await bot.send_message(message.from_user.id, 'Подписка на полное расписание успешно оформлена.',
                           reply_markup=generate_keyboard_sub_rasp(message.from_user.id))


async def unsubscribe_to_all_rasp(message: types.CallbackQuery):
    await del_message(message)

    unsubscribe_to_all_rasp_bd(message.from_user.id)
    await bot.send_message(message.from_user.id, 'Вы успешно отписались от всего расписания.',
                           reply_markup=generate_keyboard_sub_rasp(message.from_user.id))


async def get_lastname_teacher(message: types.CallbackQuery):
    await RegistrationRasp.lastname.set()
    await bot.send_message(message.from_user.id, 'Введите вашу фамилию и инициалы. Например вы - '
                                                 'Любовь Ивановна Кисова. В поле нужно записать "КисоваЛИ"')


async def registration_teacher(message: types.Message, state):
    if len(message.text.strip().lower().replace(' ', '').replace('.', '')) < 6:
        await bot.send_message(message.from_user.id, 'Ввод некорректнет, попробуйте снова!')
        return

    lastname = message.text.strip().lower().replace(' ', '').replace('.', '')

    insert_data_teacher(lastname, message.from_user.id)
    subscribe_to_teacher_bd(message.from_user.id)

    await bot.send_message(message.from_user.id, 'Подписка на расписание преподавателя успешно оформлена.',
                           reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(message.from_user.id, settings_rasp_menu_text,
                           reply_markup=generate_keyboard_sub_rasp(message.from_user.id))
    await state.finish()


async def unsubscribe_to_teacher(message: types.CallbackQuery):
    await del_message(message)

    unsubscribe_to_teacher_bd(message.from_user.id)
    delete_teacher(message.from_user.id)

    await bot.send_message(message.from_user.id, 'Вы успешно отписались от расписания преподавателя.',
                           reply_markup=generate_keyboard_sub_rasp(message.from_user.id))


async def get_level_student(message: types.CallbackQuery):
    await RegistrationRasp.level.set()
    await bot.send_message(message.from_user.id, 'На каком курсе вы обучаетесь?', reply_markup=level_student)


async def get_form_group_name(message: types.Message):
    if message.text not in ['1', '2', '3', '4']:
        await bot.send_message(message.from_user.id, 'Ввод некорректнет, попробуйте снова!')
        return

    keyboard = generate_groups_keyboard(get_group(message.text))

    await bot.send_message(message.from_user.id, 'Выбирете вашу группу на клавиатуре', reply_markup=keyboard)
    await RegistrationRasp.group_name.set()


async def registration_student(message: types.Message, state):
    if not check_group_name(message.text):
        await bot.send_message(message.from_user.id, 'Такой группы не существует, попробуйте снова')
        await RegistrationRasp.group_name.set()
        return

    insert_data_student(message.text, message.from_user.id)
    subscribe_to_student_bd(message.from_user.id)
    await bot.send_message(message.from_user.id, f'Подписка на группу {message.text} успешно оформлена.',
                           reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(message.from_user.id, settings_rasp_menu_text,
                           reply_markup=generate_keyboard_sub_rasp(message.from_user.id))
    await state.finish()


async def unsubscribe_to_student(message: types.CallbackQuery):
    await del_message(message)

    unsubscribe_to_student_bd(message.from_user.id)
    delete_student(message.from_user.id)
    await bot.send_message(message.from_user.id, 'Вы успешно отписались от расписания студента.',
                           reply_markup=generate_keyboard_sub_rasp(message.from_user.id))


def register_subscribe_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(subscribe_to_all_rasp, text='subscribe_to_all_rasp')
    dp.register_callback_query_handler(unsubscribe_to_all_rasp, text='unsubscribe_to_all_rasp')

    dp.register_callback_query_handler(unsubscribe_to_teacher, text='unsubscribe_to_teacher')
    dp.register_callback_query_handler(get_lastname_teacher, text='subscribe_to_teacher', state=None)
    dp.register_message_handler(registration_teacher, state=RegistrationRasp.lastname)

    dp.register_callback_query_handler(unsubscribe_to_student, text='unsubscribe_to_group')
    dp.register_callback_query_handler(get_level_student, text='subscribe_to_group', state=None)
    dp.register_message_handler(get_form_group_name, state=RegistrationRasp.level)
    dp.register_message_handler(registration_student, state=RegistrationRasp.group_name)
