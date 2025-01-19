import os
import random
import shutil
import traceback
from asyncio import sleep as asyncio_sleep
from datetime import datetime
from hashlib import md5
from shutil import rmtree as rmtree_rmtree
from traceback import format_exc

import fitz
import requests
from PIL import Image, ImageDraw
from aiogram.types import InputFile
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, UserDeactivated

from config import *
from core.data_base.base import get_all_info_users, deactivate_sub_user, get_all_group, get_lastname_teacher, \
    get_name_group_student, update_status_teacher_sub
from core.utils_bot.rasp_utils import division, create_dir_for_day, sorted_files_by_date
from core.utils_bot.send_rasp import send_all_rasp, send_rasp_student, send_rasp_teacher
from create_bot import bot


async def convert_pdf_file(data_dict, path_png_temp, days, all_rasp_sub):
    if data_dict.get('group'):
        group_name = data_dict.get('group')

    if data_dict.get('teacher'):
        lastname = data_dict.get('teacher')
        lastname = f'{lastname[0].upper()}{lastname[1:-2]} {lastname[-2].upper()}.{lastname[-1].upper()}.'

    get_name_group_student(data_dict['id'])
    campus = 1
    for path_pdf in (temp_pdf_file_1, temp_pdf_file_2):
        doc = fitz.open(path_pdf)
        day_index = 0
        for page in doc:
            if day_index == len(days):
                break

            not_skip_file = False
            if data_dict.get('group'):
                try:
                    with open(f'{path_RF}/{days[day_index]}/{path_temp_files}/global_data', 'r', encoding='utf-8') as file:
                        global_data = eval(file.read())

                    x1, y1 = global_data[f'Campus_{campus}'][group_name]['CP_1']
                    x2, y2 = global_data[f'Campus_{campus}'][group_name]['CP_2']

                    highlight = page.add_rect_annot(fitz.Rect(x1, y1, x2, y2))
                    highlight.set_colors(fill=(0, 0, 1), stroke=(0, 0, 1))
                    highlight.update(opacity=0.4)
                    not_skip_file = True
                except KeyError:
                    ...

            if data_dict.get('teacher'):
                for inst in page.search_for(lastname):
                    x1, y1, x2, y2 = inst
                    rect = fitz.Rect(x1 - 4.1, y1 - 4.1, x2 + 4.1, y2 + 4.1)
                    highlight = page.add_rect_annot(rect)
                    highlight.set_colors(fill=(1, 0, 1), stroke=(1, 0, 1))
                    highlight.update(opacity=0.4)
                    not_skip_file = True

            if not_skip_file or all_rasp_sub:
                pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
                pix.save(f'{path_png_temp}/{campus}_{day_index}.png')
                division(f'{path_png_temp}/{campus}_{day_index}.png')
                day_index += 1
        doc.close()
        campus += 1

    for file in os.listdir(path_png_temp):
        await bot.send_photo(data_dict['id'], photo=InputFile(f'{path_png_temp}/{file}'))


async def down_files_pdf():
    """Загружаем файлы PDF с сайта. Если сайт недоступен,
     засыпаем на 10 минут до тех пор пока не заработает"""
    while True:
        try:
            response = requests.get(campus_1_pdf)
            with open(temp_pdf_file_1, 'wb') as out:
                out.write(response.content)

            response = requests.get(campus_2_pdf)
            with open(temp_pdf_file_2, 'wb') as out:
                out.write(response.content)
        except:
            await asyncio_sleep(60 * 10)
            print(format_exc())
            continue
        break


def delete_num(list_number):
    numbers = list()
    for index in range(len(list_number)):
        try:
            if list_number[index + 1] - list_number[index] < 5:
                continue
        except IndexError:
            ...
        numbers.append(list_number[index])

    return numbers


def calculate_hash_file(path_file):
    """Вычисляем hash файла, чтобы определить актуальность расписания"""
    hash_md5 = md5()
    with open(path_file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def check_hash():
    """Открываем файл с hash предыдущей проверки. Файл позволяет избежать лишней рассылки при установки обновлений.
    Совпадает - False, старый расп. Не совпадает - True, новый расп"""
    try:
        with open(path_old_hash, 'r', encoding='utf-8') as file:
            list_old_hash = eval(file.read())
    except (FileNotFoundError, SyntaxError):
        list_old_hash = ('pdf_1', 'pdf_2')

    new_hash_campus1_pdf = calculate_hash_file(temp_pdf_file_1)
    new_hash_campus2_pdf = calculate_hash_file(temp_pdf_file_2)

    if new_hash_campus1_pdf != list_old_hash[0] or new_hash_campus2_pdf != list_old_hash[1]:
        return True
    return False


def cutikY(img):
    imgRGB = img.copy()
    img = img.convert("L")
    pix = img.load()
    down = 0
    bibrik = False
    for x in range(img.width):
        if bibrik:
            break
        for y in range(img.height - 1, 0, -1):
            down = y
            if pix[x, y] < 240:
                bibrik = True
                break
    return imgRGB.crop((0, 0, img.width, down))


def merge_two_photo(path_lesson, path_time):
    """Обьединяем файл с расписанием звонков и занятий, а также рисуем черную линию между ними"""
    im_1 = Image.open(path_time)
    im_2 = Image.open(path_lesson)

    new_image = Image.new('RGB', (im_1.size[0] + im_2.size[0], im_1.size[1]), (250, 250, 250))

    new_image.paste(im_1, (0, 0))
    new_image.paste(im_2, (im_1.size[0], 0))
    d = ImageDraw.Draw(new_image)
    d.line((im_1.size[0], 0, im_1.size[0], im_1.size[1]), width=3, fill=(0, 0, 0))

    cutikY(new_image).save(path_lesson, "PNG")
    # new_image.show()


def cut_rasp(doc, data, path_rasp, days):
    """Разрезаем doc файл на расписание времени, предметов и
    сохраняем итог в папку дня, которая находится в папке корпуса"""
    index_day = 0
    for page in doc:
        if index_day == len(days):
            break

        create_dir_for_day(days[index_day])

        path_day = f'{path_RF}/{days[index_day]}/{path_rasp}'

        size = 0
        for i, group in enumerate(data[days[index_day]]):
            x1, y1 = data[days[index_day]][group]['CP_1']
            x2, y2 = data[days[index_day]][group]['CP_2']

            if i == 0:
                size = abs(x1 - x2) + 10
            if abs(x1 - x2) > size:
                x2 = x1 + size - 10
            rect_group = fitz.Rect(x1 - 1, y1, x2 - 2, y2)
            pix_group = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect_group, colorspace=fitz.csRGB)
            pix_group.save(f'{path_day}/{group.replace("/", "")}.png')

            rect_time = data[days[index_day]][group]['CP_time']
            pix_time = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect_time, colorspace=fitz.csRGB)

            path_rasp_time = f'{path_day}/temp_time.png'
            pix_time.save(path_rasp_time)

            path_rasp_lesson = f'{path_day}/{group.replace("/", "")}.png'

            merge_two_photo(path_rasp_lesson, path_rasp_time)

        pix_full_rasp = page.get_pixmap(matrix=fitz.Matrix(3, 3), colorspace=fitz.csRGB)
        pix_full_rasp.save(f'{path_day}/fullrasp.png')
        division(f'{path_day}/fullrasp.png')
        index_day += 1
        os.remove(path_rasp_time)


def get_data_pdf(doc, all_group, days):
    data = {}
    column = {}
    rows_group = {}
    rows_row = {}

    index = 0
    for page in doc:
        if index == len(days):
            break

        column[days[index]] = {}
        rows_group[days[index]] = {}
        data[days[index]] = {}
        rows_row[days[index]] = []

        # получаем y1 координату
        for coordinates in page.search_for('Группа:'):
            rows_row[days[index]].append(int(coordinates[1]))

        # ищем каждую группу на странице, чтобы достать координаты
        for group in all_group:
            try:
                coordinates = page.search_for(group[0])
            except (ValueError, IndexError):
                continue

            if len(coordinates) == 0:
                continue
            elif len(coordinates) == 1:
                x1, y1, x2, y2 = coordinates[0]
            else:
                for coordinate in coordinates:
                    x1, y1, x2, y2 = coordinate
                    text_list = page.get_textbox((x1, y1, x2 + 14, y2)).split('\n')
                    if group[0] in text_list:
                        break

            # создаем координаты 1 точки для обрезки для каждой группы
            data[days[index]][group[0]] = {}
            data[days[index]][group[0]]['CP_1'] = (int(x1), int(y1))

            # если нет - создаем ключ, иначе обращаемся по ключу и прибавляем к переменной 1

            if int(x1) not in column[days[index]]:
                column[days[index]][int(x1)] = 1
            else:
                column[days[index]][int(x1)] += 1

            if int(y1) not in rows_group[days[index]]:
                rows_group[days[index]][int(y1)] = 1
            else:
                rows_group[days[index]][int(y1)] += 1

        index += 1

    for day in column:
        column[day] = sorted(column[day])
        column[day] = delete_num(column[day])

        rows_group[day] = sorted(rows_group[day])
        rows_group[day] = delete_num(rows_group[day])

    # забираем координаты времени  х1 и х2
    x1_time, x2_time = int(doc[len(days) - 1].search_for('Группа:')[0][0] - 5), int(doc[len(days) - 1].search_for('Группа:')[0][2] + 8)

    for day in column:
        for group in data[day]:

            x1, y1 = data[day][group]['CP_1']

            try:
                # берем Х2 от следующей группы
                x2 = column[day][column[day].index(x1) + 1]
            except IndexError:
                # делаем Х2 произвольно, т.к. это крайняя группа
                x2 = column[day][column[day].index(x1)] + 87
            except ValueError:
                try:
                    # находим число, которое ближе к искомому (неточности во время округления координат PDF файлов)
                    closest_number = min(column[day], key=lambda x: abs(x - x1))
                    x2 = column[day][column[day].index(closest_number) + 1]
                except:
                    x2 = column[day][-1] + 87
            try:
                y2 = rows_group[day][rows_group[day].index(y1) + 1]
            except IndexError:
                y2 = rows_group[day][rows_group[day].index(y1)] + 150
            except ValueError:
                try:
                    closest_number = min(column[day], key=lambda x: abs(x - y1))
                    y2 = column[day][column[day].index(closest_number) + 1]
                except:
                    y2 = rows_group[day][-1] + 150

            data[day][group]['CP_2'] = (x2, y2)

            data[day][group]['CP_time'] = (x1_time, y1, x2_time, y2)

    return data


def generate_rasp(all_group):
    data_global = {}
    num_campus = 0
    for file in (temp_pdf_file_1, temp_pdf_file_2):
        # открываем pdf файл и начинаем его обработку
        doc = fitz.open(file)

        # получаем дни, которые есть в pdf
        days = []
        for page in doc:
            for day in all_days:
                name_day = page.search_for(day)
                if name_day:
                    days.append(day)
                    break

        # генерируем данные для обрезки изображения
        data = get_data_pdf(doc, all_group, days)

        # удаляем уже существующие дни для обновления расписания, удаляем в 1 итерации цикла
        # (чтобы не удалить важные данные)

        if not num_campus:
            for day in days:
                if os.path.exists(f'{path_RF}/{day}'):
                    rmtree_rmtree(f'{path_RF}/{day}')

        # обрезаем расписание и сохраняем изображения
        cut_rasp(doc, data, f'{campus_dirs[num_campus]}', days)

        data_global[f'Campus_{num_campus + 1}'] = data

        doc.close()
        num_campus += 1

    for day in days:
        # сохраняем данные в файл global_data для каждого дня (нужен для получения распа при запросе пользователя)
        with open(f'{path_RF}/{day}/{path_temp_files}/global_data', 'w', encoding='utf-8') as file:
            global_data_day = {
                'Campus_1': data_global['Campus_1'][day],
                'Campus_2': data_global['Campus_2'][day]
            }
            file.write(str(global_data_day))

        # копируем файлы pdf из временной директории в папки дней (нужно для обработки запросов на расп от юзеров)
        shutil.copy2(f'{path_temp}/1.pdf', f'{path_RF}/{day}/{pdf_file_1}')
        shutil.copy2(f'{path_temp}/2.pdf', f'{path_RF}/{day}/{pdf_file_2}')

    return days


async def news():
    print('Отправка новостей')
    if not (os.path.exists(f'{path_news_files}/news_text') or os.listdir(f'{path_news_files}/photo')):
        return

    with open(f'{path_news_files}/news_text', 'r', encoding='utf-8') as file:
        text_news = file.read()

    # media = MediaGroup()
    # for file in os.listdir(f'{path_news_files}/photo'):
    #     media.attach_photo(InputFile(f'{path_news_files}/photo/{file}'))

    for user in get_all_info_users():
        try:
            await bot.send_message(user[0], text_news)
        except RetryAfter as error:
            print('Ебаный бот и ебаный спам')
            await asyncio_sleep(error.timeout)

        except (BotBlocked, ChatNotFound, UserDeactivated):
            deactivate_sub_user(user[0])
            print(f'del user {user[0]}')
            continue
        except:
            print(f'Ошибка {user[0]}\n{format_exc()}')
        await asyncio_sleep(random.randint(1, 2))


def del_old_days():
    """Функция удаляет самые старые дни, если их накопилось более 3"""
    sorted_files = sorted_files_by_date()

    if len(sorted_files) > 3:
        while len(os.listdir(path_RF)) > 3:
            print(f'delete path - {path_RF}/{sorted_files[-1][0]}')
            rmtree_rmtree(f'{path_RF}/{sorted_files[-1][0]}')
            sorted_files.pop(-1)


async def sending_messages():
    all_group = get_all_group()

    # await news()

    while True:
        await down_files_pdf()

        if check_hash():
            await bot.send_message(general_admin, f"\nНовый расп: {datetime.now()}\n")
            print(f"\nНовый расп: {datetime.now()}\n")

            with open(path_old_hash, 'w', encoding='utf-8') as file:
                file.write(str((calculate_hash_file(temp_pdf_file_1), calculate_hash_file(temp_pdf_file_2))))

            try:
                del_old_days()
                days = generate_rasp(all_group)
            except:
                await bot.send_message(general_admin, f"Ошибка при формировании расписания\n{traceback.format_exc()}")
                del_old_days()
                days = generate_rasp(all_group)

            for user in get_all_info_users():
                id_tg, group_sub, teacher_sub, all_rasp_sub = user
                try:
                    match (group_sub, teacher_sub, all_rasp_sub):
                        case 0, 0, 0:
                            continue

                        case 1, 0, 0:
                            await send_rasp_student(id_tg, days)

                        case 0, 0, 1:
                            await send_all_rasp(id_tg, days)

                        case 0, 1, 0:
                            lastname = get_lastname_teacher(id_tg)

                            if lastname:
                                path_day = f'{path_temp}/{id_tg}_mailing_teacher'
                                os.mkdir(path_day)
                                await send_rasp_teacher(lastname, path_day, id_tg, days, mailing=True)
                                rmtree_rmtree(path_day)
                            else:
                                update_status_teacher_sub(id_tg)
                                print(f'update {id_tg}')
                                continue

                        case 0 | 1, 0 | 1, 0 | 1:
                            data_dict = {'group': get_name_group_student(id_tg), 'teacher': get_lastname_teacher(id_tg),
                                         'id': id_tg}

                            path_day = f'{path_RF}/{days[0]}/{path_temp_files}/{id_tg}'

                            if os.path.exists(path_day):
                                rmtree_rmtree(path_day)

                            os.mkdir(path_day)
                            await convert_pdf_file(data_dict, path_day, days, all_rasp_sub)
                            rmtree_rmtree(path_day)

                    await asyncio_sleep(random.random() + random.randint(0, 1))

                except (BotBlocked, ChatNotFound, UserDeactivated):
                    deactivate_sub_user(id_tg)
                    print(f'Бота заблокировали: {id_tg}')
                    continue

                except RetryAfter as error:
                    print('Spam telegram detected')
                    await asyncio_sleep(error.timeout)

                except:
                    error_data = f'Пользователь{id_tg}\nДанные: {user}\n\n{format_exc()}'
                    await bot.send_message(general_admin, error_data)
                    print(error_data)
                    continue
            if 17 > datetime.now().hour > 10:
                while True:
                    await asyncio_sleep(10)
                    if datetime.now().hour > 17:
                        break
                continue

        time_now = datetime.now().hour

        if time_now > 17 or time_now < 10:
            while True:
                await asyncio_sleep(10)
                time_now = datetime.now().hour
                if 7 < time_now < 17:
                    break
        else:
            await asyncio_sleep(60)
