import os

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import path_RF
from core.utils_bot.rasp_utils import sorted_files_by_date

level_student = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='1'
        ),
        KeyboardButton(
            text='2'
        ),
        KeyboardButton(
            text='3'
        ),
        KeyboardButton(
            text='4'
        ),
    ],
], resize_keyboard=True, one_time_keyboard=True)


number_campus = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='1'
        ),
        KeyboardButton(
            text='2'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)


def generate_cabinet_keyboard(cabinets):
    """Принимает кабинеты и генерирует клавиутуру с ними. Один ряд - 5 кнопок"""
    list_cabinet = [[]]
    row_object = 0
    for cabinet in cabinets:
        if row_object == 5:
            row_object = 0
            list_cabinet.append([])
        list_cabinet[-1].append(KeyboardButton(text=cabinet))
        row_object += 1

    return ReplyKeyboardMarkup(keyboard=list_cabinet, resize_keyboard=True, one_time_keyboard=True)


def generate_groups_keyboard(groups):
    """Принимает группы, генерирует с ними клавиатуру. Один ряд - 4 группы"""
    list_group = [[]]
    row_object = 0
    for group in groups:
        if row_object == 4:
            row_object = 0
            list_group.append([])
        list_group[-1].append(KeyboardButton(text=group[0]))
        row_object += 1

    return ReplyKeyboardMarkup(keyboard=list_group, resize_keyboard=True, one_time_keyboard=True)


def generate_days_keyboard():
    """Генерирует клавиатуру с доступными днями для рассылки расписания. Один ряд - 1 кнопка"""
    sorted_files = sorted_files_by_date()

    keyboard = []
    for file in sorted_files:
        keyboard.append([KeyboardButton(text=file[0])])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

