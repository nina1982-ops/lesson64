from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from  aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['Start'])
async def start_message(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton(text='Рассчитать')
    button_2 = types.KeyboardButton(text='Информация')
    kb.add(button_1, button_2)
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    inline_kb = InlineKeyboardMarkup()
    button_calories = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
    button_formulas = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
    inline_kb.add(button_calories, button_formulas)
    await message.answer('Выберите опцию:', reply_markup=inline_kb)

@dp.callback_query_handler(text ='formulas')
async def get_formulas(call):
    formula_message = (
            "Формула Миффлина-Сан Жеора:\n"
            "Для мужчин: BMR = 10 * вес + 6.25 * рост - 5 * возраст + 5\n"
            "Для женщин: BMR = 10 * вес + 6.25 * рост - 5 * возраст - 161"
        )
    await call.answer()
    await call.message.answer(formula_message)

@dp.callback_query_handler(text = 'calories')
async def set_age(call):
    await UserState.age.set()
    await call.answer()
    await call.message.answer('Введите свой возраст:')

@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    bmr = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f'Ваша норма калорий: {bmr} ккал. ')
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

