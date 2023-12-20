import config
from aiogram import Bot,Dispatcher,types, executor
from aiogram.dispatcher.filters import Text
from db import Database
from datetime import datetime
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress
import keyboard

user_data = {}
bot = Bot(token=config.TOKEN)
kd = Dispatcher(bot)
db = Database('shop.db')

async def update_num_text(message: types.Message, new_value: int):
    with suppress(MessageNotModified):
        await message.edit_text(f"Укажите число: {new_value}", reply_markup=keyboard.get_keyboard())

@kd.message_handler(commands=['start'])
async def qwezxc(message: types.Message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text = 'Меню',callback_data="menu"))
    await message.answer("Привет!\nВыберите кнопку под сообщением чтобы продолжить.", reply_markup=markup)

@kd.callback_query_handler(text = 'menu')
async def menu(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Мой баланс", callback_data="balance_value"))
    keyboard.add(types.InlineKeyboardButton(text="Пополнить баланс", callback_data="balance_add"))
    keyboard.add(types.InlineKeyboardButton(text="Список товаров", callback_data="towars"))
    keyboard.add(types.InlineKeyboardButton(text="История покупок", callback_data="historybuy"))
    await call.message.answer("Привет!\nВыберите кнопку под сообщением чтобы продолжить.", reply_markup=keyboard)
    
@kd.callback_query_handler(text="balance_value")
async def balance(call: types.CallbackQuery):
    balances = db.get_balance(call.from_user.id)
    await call.message.answer(f"Ваш баланс: {balances} $ ")
    await call.answer(text=(f"Ваш баланс: {balances} $ "), show_alert=True)
    
@kd.callback_query_handler(text="balance_add")
async def cmd_numbers(call: types.CallbackQuery):
    user_data[call.from_user.id] = 0
    await call.message.answer("Укажите насколько хотите пополнить баланс: 0", reply_markup=keyboard.get_keyboard())
    
@kd.callback_query_handler(text="historybuy")
async def balance(call: types.CallbackQuery):
    historybuy = db.my_history(call.from_user.id)
    await call.message.answer(historybuy)

@kd.callback_query_handler(text = 'towars')
async def towars(call: types.CallbackQuery):
    data = db.categories()
    markup = types.InlineKeyboardMarkup()
    for item in data:
        id, type = item
        markup.add(types.InlineKeyboardButton(type, callback_data=f'category_{id}'))
    markup.add(types.InlineKeyboardButton('Назад', callback_data='nazad'))
    await call.message.answer("Выберите категорию товаров:", reply_markup=markup)
    
@kd.callback_query_handler(Text(startswith="category_"))
async def categories(call: types.CallbackQuery):
    category_id = call.data.split("_")[1] 
    data = db.categories_spis(category_id)

    markup = types.InlineKeyboardMarkup()
    for item in data:
        item_id, item_name = item
        markup.add(types.InlineKeyboardButton(item_name, callback_data=f'item_{item_id}'))
    markup.add(types.InlineKeyboardButton('Назад', callback_data='nazad'))
    await call.message.answer("Выбрал?", reply_markup=markup)
        
@kd.callback_query_handler(Text(startswith="item_"))
async def item(call: types.CallbackQuery):
    item_id = call.data.split("_")[1] 
    data = db.items(item_id)
    item_name, item_price = data
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Купить', callback_data=f'buy_{item_id}'))
    markup.add(types.InlineKeyboardButton('Назад', callback_data='nazad'))
    await call.message.answer(f"Название: {item_name}\nЦена: {item_price}", reply_markup=markup)

@kd.callback_query_handler(Text(startswith="num_"))
async def callbacks_num(call: types.CallbackQuery):
    user_value = user_data.get(call.from_user.id, 0)
    action = call.data.split("_")[1]
    if action == "incr":
        user_data[call.from_user.id] = user_value+100
        await update_num_text(call.message, user_value+100)
    elif action == "decr":
        user_data[call.from_user.id] = user_value-100
        await update_num_text(call.message, user_value-100)
    elif action == "finish":
        await call.message.edit_text(f"Вы успешно пополнили баланс на: {user_value}")
        db.add_balance(call.from_user.id, user_value)
    await call.answer()
    
@kd.callback_query_handler(Text(startswith='buy_'))
async def buy(call: types.CallbackQuery):
    balances = db.get_balance(call.from_user.id)
    item_id = call.data.split("_")[1]
    towars_price = db.tow_price(item_id)
    date = datetime.now()   
    tow_price = []

    for string in towars_price:
        string = str(string)
        cleaned_string = string.replace("(", "").replace(")", "").replace(",", "").replace("'", "").strip()
        tow_price.append(cleaned_string)
    
    if balances >= towars_price:
        db.remove_balance(call.from_user.id,tow_price[0])
        db.history_add(call.from_user.id, item_id, date)
        await call.message.answer("Вы успешно купили товар!")
    else:
        await call.message.answer("У вас недостаточно средств!")
        
@kd.callback_query_handler(text= 'nazad')
async def nazad(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Мой баланс", callback_data="balance_value"))
    keyboard.add(types.InlineKeyboardButton(text="Пополнить баланс", callback_data="balance_add"))
    keyboard.add(types.InlineKeyboardButton(text="Список товаров", callback_data="towars"))
    keyboard.add(types.InlineKeyboardButton(text="История покупок", callback_data="historybuy"))
    await call.message.answer("Выберите кнопку под сообщением чтобы продолжить.", reply_markup=keyboard)
    
@kd.message_handler()
async def process_message(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)

if __name__ == "__main__":
    print("Starting...", end='')
    executor.start_polling(kd, skip_updates=True)
    