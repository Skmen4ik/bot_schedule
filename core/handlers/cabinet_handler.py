import os
import traceback

import fitz
from aiogram import Dispatcher, types
from aiogram.types import InputFile

from config import pdf_file_1, pdf_file_2, path_RF, path_temp, name_statistic_func
from core.data_base.base import get_cabinets_bd, add_data_statistic
from core.keyboards.inline import rasp_menu
from core.keyboards.simple import number_campus, generate_cabinet_keyboard, generate_days_keyboard
from core.utils_bot.classes_state import GetStatusCabinet
from core.utils_bot.rasp_utils import division, delete_keyboard
from create_bot import bot


async def get_campus_cabinet(message: types.Message):
    await bot.send_message(message.from_user.id, 'На какой день нужно расписание?', reply_markup=generate_days_keyboard())
    await GetStatusCabinet.day.set()


async def get_day_cabinet(message: types.Message, state):
    if message.text not in os.listdir(path_RF):
        await bot.send_message(message.from_user.id,
                               'Такого дня не существует, попробуйте снова!',
                               reply_markup=generate_days_keyboard())

    async with state.proxy() as data:
        data['day'] = message.text

    await bot.send_message(message.from_user.id, 'Выберете корпус, в котором находится кабинет', reply_markup=number_campus)
    await GetStatusCabinet.campus.set()


async def get_cabinet(message: types.Message, state):
    if message.text not in ['1', '2']:
        await bot.send_message(message.from_user.id, 'Ввод не коректен, попробуйте снова')
        return

    cabinets = get_cabinets_bd(message.text)

    async with state.proxy() as data:
        data['campus'] = message.text
        data['cabinets'] = cabinets

    await bot.send_message(message.from_user.id, 'Выберете кабинет на клавиатуре',
                           reply_markup=generate_cabinet_keyboard(cabinets))
    await GetStatusCabinet.cabinet.set()


async def get_rasp_cabinet(message: types.Message, state):
    async with state.proxy() as data:
        if message.text not in data['cabinets']:
            await bot.send_message(message.from_user.id, 'Такого кабинета не существует, попробуйте снова!', reply_markup=rasp_menu)
            await state.finish()
            return
        num_campus = data['campus']
        day = data['day']
    try:
        if num_campus == '1':
            doc = fitz.open(f'{path_RF}/{day}/{pdf_file_1}')
        else:
            doc = fitz.open(f'{path_RF}/{day}/{pdf_file_2}')

        list_files = []

        num_file = 1
        for page in doc:
            if message.text.isdigit():
                finding_text = page.search_for(f'{message.text}/{num_campus}')
            else:
                finding_text = page.search_for(message.text)
            if len(finding_text) == 0:
                continue

            for x1, y1, x2, y2 in finding_text:

                text = page.get_textbox((x1 - 7, y1, x2 + 7, y2)).split('\n')

                text_list = []

                for element in text:
                    text_list += element.split(' ')

                if f'{message.text}/{num_campus}' not in text_list:
                    continue

                rect = fitz.Rect(x1, y1, x2, y2)
                highlight = page.add_rect_annot(rect)
                highlight.set_colors(fill=(1, 0, 1), stroke=(1, 0, 1))
                highlight.update(opacity=0.4)

            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
            path = f'{path_temp}/{message.from_user.id}_{num_file}.png'
            pix.save(path)
            division(path)
            list_files.append(path)
            num_file += 1

        doc.close()

        if len(list_files) == 0:
            await bot.send_message(message.from_user.id, f'Ничего не найдено по кабинету {message.text} =(=', reply_markup=rasp_menu)
        elif len(list_files) == 1:
            await bot.send_photo(message.from_user.id, photo=InputFile(list_files[0]), reply_markup=rasp_menu)
        else:
            for file in list_files:
                if file == list_files[-1]:
                    await bot.send_photo(message.from_user.id, photo=InputFile(list_files[0]), reply_markup=rasp_menu)
                else:
                    await bot.send_photo(message.from_user.id, photo=InputFile(list_files[0]))

        for path in list_files:
            os.remove(path)

        add_data_statistic(name_statistic_func, 'cabinets')
    except:
        error = traceback.format_exc()
        print(error)
        add_data_statistic(name_statistic_func, 'cabinets_errors')
        await bot.send_message(message.from_user.id, error, reply_markup=rasp_menu)
    await state.finish()
    await delete_keyboard(message)


def register_cabinet_handlers(dp: Dispatcher):
    dp.register_message_handler(get_campus_cabinet, commands=['get_cab'], state=None)
    dp.register_message_handler(get_day_cabinet, state=GetStatusCabinet.day)
    dp.register_message_handler(get_cabinet, state=GetStatusCabinet.campus)
    dp.register_message_handler(get_rasp_cabinet, state=GetStatusCabinet.cabinet)
