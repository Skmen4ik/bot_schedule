import os
from os import mkdir
from os.path import exists

from aiogram import types
from aiogram.utils.exceptions import MessageToDeleteNotFound

from config import path_RF, path_pdf_files, path_rasp_files, path_temp_files

from PIL import Image

from create_bot import bot


def division(path):
    """Функция принимает путь до файла с полным расписанием и обрезает весь не нужный белый фон"""
    image = Image.open(path)
    imageRGB = image
    image = image.convert("L")
    width = image.size[0]
    height = image.size[1]
    pix = image.load()

    count = 0
    end = False
    for y in range(height - 1, 0, -1):
        if end:
            break
        for x in range(0, width):
            if pix[x, y] < 250:
                count += 1
            else:
                count = 0
            if count > 50:
                s = y + 1
                end = True
                break

    count = 0
    end = False
    w2 = -1000
    for y in range(0, height):
        if end:
            break
        for x in range(0, width):
            if pix[x, y] < 250:
                count += 1
                if w2 == -1000:
                    w2 = y - 1
            else:
                count = 0
            if count > 50:
                w = y - 1
                end = True
                break

    count = 0
    end = False
    for x in range(0, width):
        if end:
            break
        for y in range(0, height):
            if pix[x, y] < 250:
                count += 1
            else:
                count = 0
            if count > 50:
                a = x - 1
                end = True
                break

    count = 0
    end = False
    for x in range(width - 1, 0, -1):
        if end:
            break
        for y in range(0, height):
            if pix[x, y] < 250:
                count += 1
            else:
                count = 0
            if count > 50:
                d = x + 1
                end = True
                break

    res = imageRGB.crop((a, w2 - 10, d, s))
    res.save(path)


def create_dir_for_day(day):
    """Функция принимает название дня, а затем создает для этого дня все нужные директории:
    temp_files, pdf_files, data_rasp_photo"""
    path_day = f'{path_RF}/{day}'
    for dir_file in (path_day,
                     f'{path_day}/{path_pdf_files}', f'{path_day}/{path_rasp_files}', f'{path_day}/{path_temp_files}',
                     f'{path_day}/{path_pdf_files}/Campus_1', f'{path_day}/{path_pdf_files}/Campus_2',
                     f'{path_day}/{path_rasp_files}/Campus_1', f'{path_day}/{path_rasp_files}/Campus_2'):
        if not exists(dir_file):
            mkdir(dir_file)


def sorted_files_by_date():
    """Функция создает список из дней с распом и временем их создания, а возвращает список от новых до старых дней"""
    filelist = [(file, os.path.getctime(os.path.join(path_RF, file))) for file in os.listdir(path_RF)]

    return sorted(filelist, key=lambda x: x[1], reverse=True)


async def delete_keyboard(message: types.Message):
    """Функция создана для удаления обычной клавиатуры"""
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    except MessageToDeleteNotFound:
        ...
