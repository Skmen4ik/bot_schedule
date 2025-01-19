from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationRasp(StatesGroup):
    level = State()
    group_name = State()
    lastname = State()


class GetStatusCabinet(StatesGroup):
    day = State()
    campus = State()
    cabinet = State()


class GetStatusGroup(StatesGroup):
    day = State()
    campus = State()
    group_name = State()


class GetDayStudent(StatesGroup):
    day = State()


class GetDayAllRasp(StatesGroup):
    day = State()


class GetDayTeacherOne(StatesGroup):
    day = State()


class GetDayTeacher(StatesGroup):
    day = State()
