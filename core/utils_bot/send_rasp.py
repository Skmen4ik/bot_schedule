import os

import fitz
from aiogram import types
from aiogram.types import InputFile

from config import pdf_file_1, pdf_file_2, path_RF
from core.data_base.base import get_name_group_student
from core.keyboards.inline import generate_keyboard_getting_rasp, rasp_menu, main_menu
from core.utils_bot.rasp_utils import division
from create_bot import bot


async def del_message(message: types.CallbackQuery):
    try:
        await message.message.delete()
    except:
        pass
    # MessageCantBeDeleted


async def send_all_rasp(id_tg, days, mailing=True, button_start=False):
    send_message = []
    for num_campus in (1, 2):
        for day in days:
            photo = InputFile(f'{path_RF}/{day}/data_rasp_photo/Campus_{num_campus}/fullrasp.png')
            send_message.append((day, photo, num_campus))

    index = 1
    for name_day, photo, campus in send_message:
        if mailing or len(send_message) != index:
            await bot.send_photo(id_tg, photo=photo, caption=f'{campus} корпус, {name_day}')
        else:
            if button_start:
                await bot.send_photo(id_tg, photo=photo, caption=f'{campus} корпус, {name_day}',
                                     reply_markup=generate_keyboard_getting_rasp(id_tg))
            else:
                await bot.send_photo(id_tg, photo=photo, caption=f'{campus} корпус, {name_day}',
                                     reply_markup=rasp_menu)
        index += 1


async def send_rasp_student(id_telegram, days, mailing=True, command=False, group_student=''):
    if not command:
        group_student = get_name_group_student(id_telegram)

    flag = True
    for num_campus in (1, 2):
        i = 1
        for day in days:

            path = f'{path_RF}/{day}/data_rasp_photo/Campus_{num_campus}'
            try:
                photo = InputFile(f"{path}/{group_student.replace('/', '')}.png")
            except:
                continue
            flag = False
            if day == days[-1] and not mailing:
                await bot.send_photo(chat_id=id_telegram, photo=photo, caption=day,
                                     reply_markup=generate_keyboard_getting_rasp(id_telegram))
            else:
                await bot.send_photo(chat_id=id_telegram, photo=photo, caption=day)
            i += 1
    if flag:
        await bot.send_message(id_telegram, f'Для группы <u>{group_student}</u> расписание найдено не было.',
                               reply_markup=main_menu)


async def send_rasp_teacher(lastname, path_png_temp, id_tg, days, mailing=False):
    lastname = f'{lastname[0].upper()}{lastname[1:-2]} {lastname[-2].upper()}.{lastname[-1].upper()}.'
    list_paths = []
    campus = 1
    path_day_pdf = f'{path_RF}/{days[0]}'
    for path_pdf in (f'{path_day_pdf}/{pdf_file_1}', f'{path_day_pdf}/{pdf_file_2}'):
        doc = fitz.open(path_pdf)
        day_index = 0
        for page in doc:
            finding_text = page.search_for(lastname)
            if len(finding_text) == 0:
                continue

            for inst in finding_text:
                x1, y1, x2, y2 = inst
                rect = fitz.Rect(x1 - 4.1, y1 - 4.1, x2 + 4.1, y2 + 4.1)
                highlight = page.add_rect_annot(rect)
                highlight.set_colors(fill=(1, 0, 1), stroke=(1, 0, 1))
                highlight.update(opacity=0.4)

            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
            pix.save(f'{path_png_temp}/{campus}_{day_index}.png')
            division(f'{path_png_temp}/{campus}_{day_index}.png')
            list_paths.append(f'{path_png_temp}/{campus}_{day_index}.png')
            day_index += 1

        doc.close()
        campus += 1

    num_file = 1
    if not len(list_paths):
        if mailing:
            await bot.send_message(id_tg, f'Расписание для {lastname} не найдено!\n')
        else:
            await bot.send_message(id_tg, f'Расписание для {lastname} не найдено!\n', reply_markup=rasp_menu)
        return
    for path in list_paths:
        if mailing:
            await bot.send_photo(id_tg, photo=InputFile(path))
        else:
            if len(list_paths) == num_file:
                await bot.send_photo(id_tg, photo=InputFile(path), reply_markup=rasp_menu)
            else:
                await bot.send_photo(id_tg, photo=InputFile(path))
        num_file += 1
