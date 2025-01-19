from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.data_base.base import check_subscribe_to_all_rasp, check_subscribe_to_teacher, check_subscribe_to_group, \
    get_data_all_subs_user

to_main_rasp = InlineKeyboardButton(
    text='🔙Вернуться в меню расписания◀️',
    callback_data='get_rasp_menu'
)

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Расписание',
            callback_data='get_rasp_menu'
        ),
        InlineKeyboardButton(
            text='Что-то на потом...',
            callback_data='Что-то на потом...'
        )
    ]
])


rasp_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Настроить рассылку',
            callback_data='menu_settings_rasp'
        ),
    ],
    [
        InlineKeyboardButton(
            text='Получить расписание',
            callback_data='menu_get_rasp'
        )
    ],
    [
        InlineKeyboardButton(
            text='В главное меню',
            callback_data='to_main_menu'
        )
    ]
])

back_main_menu_o = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='В главное меню',
            callback_data='to_main_menu'
        )
    ]
])


def generate_keyboard_sub_rasp(id_tg):
    """Функция генерирует клавиатуру с подпиской на расписание для пользователя с id_tg"""
    if check_subscribe_to_all_rasp(id_tg):
        button_all_rasp = InlineKeyboardButton(
            text='🎆Отписаться от полного расписания⛔️',
            callback_data='unsubscribe_to_all_rasp'
        )
    else:
        button_all_rasp = InlineKeyboardButton(
            text='🎆Подписаться на полное расписание✅',
            callback_data='subscribe_to_all_rasp'
        )

    if check_subscribe_to_teacher(id_tg):
        button_teacher = InlineKeyboardButton(
            text='👨‍🏫Отписаться от преподавателя⛔️',
            callback_data='unsubscribe_to_teacher'
        )
    else:
        button_teacher = InlineKeyboardButton(
            text='👨‍🏫Подписаться на преподавателя✅',
            callback_data='subscribe_to_teacher'
        )

    if check_subscribe_to_group(id_tg):
        button_group = InlineKeyboardButton(
            text='🎓Отписаться от группы⛔️',
            callback_data='unsubscribe_to_group'
        )
    else:
        button_group = InlineKeyboardButton(
            text='🎓Подписаться на группу✅',
            callback_data='subscribe_to_group'
        )

    return InlineKeyboardMarkup(inline_keyboard=[
        [button_all_rasp],
        [button_teacher],
        [button_group],
        [to_main_rasp]
        ])


def generate_keyboard_getting_rasp(id_tg):
    """Функция генерирует клавиатуру с получем расписанием для пользователя с id_tg"""
    teacher, student = get_data_all_subs_user(id_tg)
    keyboard = [[InlineKeyboardButton(
        text='Получить полное расписание🎆',
        callback_data='get_all_rasp'
    )]]
    if teacher:
        keyboard.append([
            InlineKeyboardButton(
                text='Получить расписание преподавателя👨‍🏫',
                callback_data='get_rasp_teacher'
            )
        ])
    if student:
        keyboard.append([InlineKeyboardButton(
            text='Получить расписание студента🎓',
            callback_data='get_rasp_student'
        )])
    keyboard.append([to_main_rasp])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
