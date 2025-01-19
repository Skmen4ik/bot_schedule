import sqlite3 as sq
from itertools import chain

from config import path_groups_student, path_cabinet_data, time_to_backup_bd
from datetime import datetime
from asyncio import sleep as asyncio_sleep


# запуск БД
def start_db():
    """Создает таблицы БД и делает глобальный доступ переменных для доступа к ней"""
    global base, cursor
    base = sq.connect('database.db')
    base.execute('PRAGMA foreign_keys = ON')
    if base:
        print('BD ONLINE')
    cursor = base.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS Users '
                   '(id_telegram PRIMARY KEY, '
                   'subscription_student INTEGER DEFAULT 0,'
                   'subscription_teacher INTEGER DEFAULT 0, '
                   'subscription_all_rasp INTEGER DEFAULT 0)')
    base.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS Users_teachers '
                   '(id_user INTEGER, lastname VARCHAR(20), FOREIGN KEY(id_user) REFERENCES '
                   'Users(id_telegram) ON DELETE CASCADE)')
    base.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS Groups(id_group INTEGER PRIMARY KEY AUTOINCREMENT,'
                   ' group_name VARCHAR(15) UNIQUE, level INTEGER)')
    base.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS Users_groups '
                   '(id_user INTEGER UNIQUE, id_group INTEGER,'
                   'FOREIGN KEY (id_user) REFERENCES Users(id_telegram) ON DELETE CASCADE)')
    base.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS Statistic_func '
                   '(all_rasp INTEGER DEFAULT 0, all_rasp_errors INTEGER DEFAULT 0 ,'
                   'teacher INTEGER DEFAULT 0, teacher_errors INTEGER DEFAULT 0, '
                   'student INTEGER DEFAULT 0, student_errors INTEGER DEFAULT 0,'
                   'cabinets INTEGER DEFAULT 0, cabinets_errors INTEGER DEFAULT 0,'
                   'date_start) ')
    base.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS Statistic_button '
                   '(all_rasp INTEGER DEFAULT 0, all_rasp_errors INTEGER DEFAULT 0 ,'
                   'teacher INTEGER DEFAULT 0, teacher_errors INTEGER DEFAULT 0, '
                   'student INTEGER DEFAULT 0, student_errors INTEGER DEFAULT 0,'
                   'date_start) ')
    base.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS Cabinets(cabinet_name VARCHAR(15), campus INTEGER)')
    base.commit()


def get_all_group():
    """Получаем весь список групп. Список групп нужен для поиска групп в PDF файле"""
    return cursor.execute('SELECT group_name FROM Groups').fetchall()


def update_groups_info():
    """Скрипт обновления информации о группах. Если таблица с группами не содержит записей,
    скрипт считывает файл с группами и вносит информацию в БД. Файл содержит наименование группы,
    а через пробел ее курс."""
    id_1 = bool(cursor.execute('SELECT count(*) FROM Groups').fetchone()[0])

    if not id_1:
        with open(path_groups_student, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                cursor.execute('INSERT INTO Groups (group_name, level) VALUES (?, ?)', line.split(' '))
                base.commit()


def update_cabinet_name():
    """Скрипт обновления информации о кабинетах. Если таблица с кабинетами не содержит записей,
    скрипт считывает файл с кабинетами и вносит информацию в БД. Файл содержит наименование кабинета,
    а через пробел его корпус."""
    id_1 = bool(cursor.execute('SELECT count(*) FROM Cabinets').fetchone()[0])

    if not id_1:
        with open(path_cabinet_data, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                cursor.execute('INSERT INTO Cabinets (cabinet_name, campus) VALUES (?, ?)', line.split(' '))
                base.commit()


def get_cabinets_bd(number_campus):
    """Принимает номер корпуса и возвращает все кабинеты для него. Нужно для генерации клавиатуру пользователю"""
    return list(chain.from_iterable(
        cursor.execute('SELECT cabinet_name FROM Cabinets WHERE campus = ?', (number_campus,)).fetchall()))


def check_user_in_users(id_tg):
    """Функция принимает id telegram пользователя и проверяет его в БД. Нужна для избежания перезаписи инфы о
    пользователя, когда он нажимает несколько раз команду /start, а также для регистрации, чтобы избежать ошибок"""
    return bool(cursor.execute('SELECT 1 FROM Users WHERE id_telegram = ?', (id_tg,)).fetchone())


def registration_user(id_tg):
    """Регистрирует пользователя в БД с id telegram. Срабатывает либо после команды /start, либо после нажатий на
    клавиатуру в боте. Необходима чаще всего для избежания ошибок, когда пользователь в БД отсутствует,
    а в БД он должен быть для генерации клавиатур и прочего функционала"""
    cursor.execute("INSERT INTO Users (id_telegram) VALUES (?)", (id_tg,))
    base.commit()


def check_subscribe_to_all_rasp(id_tg):
    """Проверяет подписку на полное расписание для пользователя с id telegram. Используется для генерации клавиатуры
    в меню подписок на полное, студенческое и преподавательское расписание"""
    return bool(cursor.execute('SELECT subscription_all_rasp FROM Users WHERE id_telegram = ? ',
                               (id_tg,)).fetchone()[0])


def check_subscribe_to_teacher(id_tg):
    """Проверяет подписку на расписание препода для пользователя с id telegram. Используется для генерации клавиатуры
    в меню подписок на полное, студенческое и преподавательское расписание"""
    return bool(cursor.execute('SELECT subscription_teacher FROM Users WHERE id_telegram = ?',
                               (id_tg,)).fetchone()[0])


def check_subscribe_to_group(id_tg):
    """Проверяет подписку на расписание студенты для пользователя с id telegram. Используется для генерации клавиатуры
    в меню подписок на полное, студенческое и преподавательское расписание"""
    return bool(cursor.execute('SELECT subscription_student FROM Users WHERE id_telegram = ?',
                               (id_tg,)).fetchone()[0])


def subscribe_to_all_rasp_bd(id_tg):
    """Подписывает пользователя на полное расписание с указанным id telegram в таблицу Users."""
    cursor.execute("UPDATE Users set subscription_all_rasp = ? WHERE id_telegram = ?", (1, id_tg))
    base.commit()


def subscribe_to_teacher_bd(id_tg):
    """Подписывает пользователя на расписание препода с указанным id telegram в таблицу Users. ФИО препода в таблицу
    Users_teachers вносятся отдельной функцией"""
    cursor.execute("UPDATE Users set subscription_teacher = ? WHERE id_telegram = ?", (1, id_tg))
    base.commit()


def subscribe_to_student_bd(id_tg):
    """Подписывает пользователя на расписание студента с указанным id telegram в таблицу Users. Наименование группы в
    таблицу Users_groups вносятся отдельной функцией"""
    cursor.execute("UPDATE Users set subscription_student = ? WHERE id_telegram = ?", (1, id_tg))
    base.commit()


def unsubscribe_to_all_rasp_bd(id_tg):
    """Отписывает пользователя от полного расписания."""
    cursor.execute("UPDATE Users set subscription_all_rasp = ? WHERE id_telegram = ?", (0, id_tg))
    base.commit()


def unsubscribe_to_teacher_bd(id_tg):
    """Отписывает пользователя от расписания препода. Данные из таблицы Users_teachers удаляются другой функцией"""
    cursor.execute("UPDATE Users set subscription_teacher = ? WHERE id_telegram = ?", (0, id_tg))
    base.commit()


def unsubscribe_to_student_bd(id_tg):
    """Отписывает пользователя от расписания студента. Данные из таблицы Users_groups удаляются другой функцией"""
    cursor.execute("UPDATE Users set subscription_student = ? WHERE id_telegram = ?", (0, id_tg))
    base.commit()


def insert_data_teacher(lastname, id_tg):
    cursor.execute("INSERT INTO Users_teachers (id_user, lastname) VALUES (?, ?)",
                   (id_tg, lastname))
    base.commit()


def delete_teacher(id_tg):
    cursor.execute('DELETE FROM Users_teachers WHERE id_user = ?', (id_tg,))
    base.commit()


def insert_data_student(lastname, id_tg):
    id_group = cursor.execute('SELECT id_group FROM Groups WHERE group_name = ?',
                              (lastname,)).fetchone()[0]
    cursor.execute("INSERT INTO Users_groups (id_user, id_group) VALUES (?, ?)",
                   (id_tg, id_group))
    base.commit()


def delete_student(id_tg):
    cursor.execute('DELETE FROM Users_groups WHERE id_user = ?', (id_tg,))
    base.commit()


def get_group(level):
    return cursor.execute('SELECT group_name FROM Groups WHERE level = ?',
                          (level,)).fetchall()


def check_group_name(group_name):
    return bool(cursor.execute('SELECT 1 FROM Groups WHERE group_name = ?', (group_name,)).fetchone())


def get_data_all_subs_user(id_tg):
    return cursor.execute('SELECT subscription_teacher, subscription_student FROM Users '
                          'WHERE id_telegram = ?', (id_tg,)).fetchone()


def get_lastname_teacher(id_tg):
    lastname = cursor.execute('SELECT lastname FROM Users_teachers WHERE id_user = ?', (id_tg,)).fetchone()
    if lastname:
        return lastname[0]


def get_name_group_student(id_tg):
    group = cursor.execute('SELECT group_name FROM Groups WHERE id_group = '
                           '(SELECT id_group FROM Users_groups WHERE id_user = ?)', (id_tg,)).fetchone()
    if group:
        return group[0]


def get_all_info_users():
    return cursor.execute('SELECT * FROM Users').fetchall()


def deactivate_sub_user(id_tg):
    cursor.execute('DELETE FROM Users WHERE id_telegram = ?', (id_tg,))
    base.commit()


def add_data_statistic(name_table, name_row):
    status = cursor.execute(f'SELECT 1 FROM {name_table} WHERE date_start = ?',
                            (datetime.date(datetime.now()),)).fetchone()
    if status:
        cursor.execute(f"UPDATE {name_table} SET {name_row} = {name_row} + 1 WHERE date_start = ?",
                       (datetime.date(datetime.now()),))
    else:
        cursor.execute(f'INSERT INTO {name_table} ({name_row},  date_start) VALUES (?, ?)',
                       (1, datetime.date(datetime.now())))
    base.commit()


def get_quantity_users():
    all_users = cursor.execute('SELECT count(*) FROM Users').fetchone()[0]
    all_teachers = cursor.execute('SELECT count(*) FROM Users_teachers').fetchone()[0]
    all_students = cursor.execute('SELECT count(*) FROM Users_groups').fetchone()[0]
    all_all_rasp = cursor.execute('SELECT count(*) FROM Users WHERE subscription_all_rasp = 1').fetchone()[0]
    no_sub_user = cursor.execute('SELECT count(*) FROM Users WHERE subscription_all_rasp = 0 AND'
                                 ' subscription_student = 0 AND subscription_teacher = 0').fetchone()[0]
    return all_users, all_teachers, all_students, all_all_rasp, no_sub_user


def get_statistic_button():
    return cursor.execute('SELECT * FROM Statistic_button').fetchall()


def get_statistic_func():
    return cursor.execute('SELECT * FROM Statistic_func').fetchall()


def update_status_teacher_sub(id_tg):
    cursor.execute('UPDATE Users SET subscription_teacher = 0 WHERE id_telegram = ?', (id_tg,))
    base.commit()


async def backup_database():
    while True:
        time = datetime.now()
        name = f'{time.date()} {time.hour}-{time.minute}'

        backup_bd = sq.connect(f'./work_files/old_bd/{name}.db')
        with backup_bd:
            base.backup(backup_bd, pages=1)
        backup_bd.close()
        await asyncio_sleep(time_to_backup_bd)
