from telegram.ext import ContextTypes
from telegram import Update
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils import deserialize_miners, check_valid_user, change_watchdog_values, WatchDogValues


miners = deserialize_miners()

menu_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('Стата', callback_data='state')],
    [InlineKeyboardButton('Перезагрузить первый асик', callback_data='reboot0')],
    [InlineKeyboardButton('Перезагрузить второй асик', callback_data='reboot1')]
    ])


async def check_asic_notification(context):
    # нужно проверить асики на ошибки
    # Если хешрейт ниже положенного или есть ошибки - 
    # Выводим ошибки

    tag = '🔴'
    
    for id, asics in miners.items():
        error_text = ''
        for asic in asics:
            name = asic.get_name()
            state = asic.get_state()
            # print(state)

            if 'error' in state:
                error_text += f"{tag} Проблема: {name} {state['error']}\n"
            if state:
                if state['hash5s'] <= asic.min_hash:
                    error_text += f'{tag} Низкий хешрейт: {name} {state["hash5s"]} {state["units"]}\n'
                for temps in list(state['temp1'] + state['temp2'] + state['temp3']):
                    if temps >= asic.max_temp:
                        error_text += f'{tag} Высокая температура: {temps} ℃\n'
            

        if error_text:
            print(error_text) #debug
            await context.bot.send_message(
                    chat_id = id,
                    text = error_text
                )


async def change_min_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'не найден' in (message := check_valid_user(update.effective_chat.id)):
        await update.message.reply_text(message)
        return
    
    await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = change_watchdog_values(update, context, miners, WatchDogValues.HASHRATE),
            reply_markup=menu_keyboard
        )
    
    
async def change_max_temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'не найден' in (message := check_valid_user(update.effective_chat.id)):
        await update.message.reply_text(message)
        return
    
    await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = change_watchdog_values(update, context, miners, WatchDogValues.TEMP),
            reply_markup=menu_keyboard
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'не найден' in (message := check_valid_user(update.effective_chat.id)):
        await update.message.reply_text(message)
        return

    query = update.callback_query
    button_data = query.data
    status = ''
    asics = miners[str(update.effective_chat.id)]

    if button_data == 'state':
        await stat(update=update, context=context)
    elif 'reboot' in button_data:
        # try:
            index = int(button_data[-1]) # взял последний символ текстового значения ответа кнопки и использую как индекс
            status = asics[index].reboot()
            answer = ''
            if status == 200:
                answer = f'{asics[index]} Перезагрузка началась'
            elif status >= 400 and status < 500:
                answer = f'{asics[index]} Ошибка на строне клиента. '
            elif status >= 500 and status < 600:
                answer = f'{asics[index]} Ошибка на строне сервера. '
            await query.answer(answer)
        # except IndexError as e:
        #     print('Error rebooting ASIC') #debug
        #     await query.answer(f'🔴 Индекс асика не найден. Error message: {e}')
    else:
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = '🔴 Invalid command',
            reply_markup=menu_keyboard
        )


async def say_hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'Пользователь не найден' in (message := check_valid_user(update.effective_chat.id)):
        await update.message.reply_text(message)
        return

    print('Hi from bot') #debug
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = 'Hi from bot',
        reply_markup=menu_keyboard
    )


async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'не найден' in (message := check_valid_user(update.effective_chat.id)):
        await update.message.reply_text(message)
        return
    
    asics = miners[str(update.effective_chat.id)]

    parsed_info = [ asic.get_message() for asic in asics ]
    print(*parsed_info) #debug
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = ' '.join(parsed_info),
        reply_markup=menu_keyboard
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, есть ли информация о чате
    if update and isinstance(update, Update):
        chat = update.effective_chat
        if chat:
            # Отправляем сообщение об ошибке в чат
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"Произошла ошибка: {context.error}"
            )