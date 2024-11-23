from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import asyncio

from crud_functions import *

users = get_all_products()

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kp2 = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton('Рассчитать')],
        [KeyboardButton('Информация')],
        [KeyboardButton('Купить')],
        [KeyboardButton('Регистрация')]
    ], resize_keyboard= True
)


kb = InlineKeyboardMarkup(resize_keyboard=True)
button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формула расчёта', callback_data='formulas')
kb.add(button)
kb.add(button2)

k1 = InlineKeyboardMarkup(resize_keyboard=True)
button_1 = InlineKeyboardButton(text='Продукт 1', callback_data='product_buying')
button_2 = InlineKeyboardButton(text='Продукт 2', callback_data='product_buying')
button_3 = InlineKeyboardButton(text='Продукт 3', callback_data='product_buying')
button_4 = InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
k1.insert(button_1)
k1.insert(button_2)
k1.insert(button_3)
k1.insert(button_4)



@dp.message_handler(text="Купить")
async def get_buying_list(message):
    with open("files/1.png", "rb") as img:
        await message.answer(f"Название: {users[0][0]} | Описание: {users[0][1]} | Цена: {users[0][2]} руб.")
        await message.answer_photo(img)
    with open("files/2.png", "rb") as img:
        await message.answer(f"Название: {users[1][0]} | Описание: {users[1][1]} | Цена: {users[1][2]} руб.")
        await message.answer_photo(img)
    with open("files/3.png", "rb") as img:
        await message.answer(f"Название: {users[2][0]} | Описание: {users[2][1]} | Цена: {users[2][2]} руб.")
        await message.answer_photo(img)
    with open("files/4.png", "rb") as img:
        await message.answer(f"Название: {users[3][0]} | Описание: {users[3][1]} | Цена: {users[3][2]} руб.")
        await message.answer_photo(img)


    await message.answer("Выберите продукт для покупки:", reply_markup=k1)



@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;'
                              'для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.')
    await call.answer()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kp2)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def get_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])
    bmr = 66 + (13.7 * weight) + (5 * growth) - (6.8 * age)
    calories = round(bmr * 1.2, 2)
    await message.answer(f'Ваша суточная норма калорий: {calories}')
    await state.finish()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()

@dp.message_handler(text="Регистрация")
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text):
        await message.answer("Пользователь существует, введите другое имя")
        await RegistrationState.username.set()
    else:
        await state.update_data(us=message.text)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(em=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(ag=message.text)
    data = await state.get_data()
    add_user(data['us'], data['em'], data['ag'])
    await message.answer("Регистрация прошла успешно. Вы умничка!")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
