from requests import Session
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CommandHandler


COINS = ["Bitcoin", 'Ethereum', "All coins", 'Litecoin']
TIME = ['24 часа', '12 часов', '1 час', '30 минут']
TOKEN2 = ''
TOKEN3 = ''


def get_coins_price():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '100',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': TOKEN2,
    }
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    data = response.json()
    coins = dict()
    for i in data['data']:
        if i['symbol'] == "ETH":
            coin_price = str(i['quote']['USD']['price'])
            if '.' in coin_price:
                coin_price = coin_price.split('.')[0]
            coins['ETH'] = f"${coin_price}"

        elif i['symbol'] == "BTC":
            coin_price = str(i['quote']['USD']['price'])
            if '.' in coin_price:
                coin_price = coin_price.split('.')[0]
            coins['BTC'] = f"${coin_price}"

        elif i['symbol'] == "LTC":
            coin_price = str(i['quote']['USD']['price'])
            if '.' in coin_price:
                coin_price = coin_price.split('.')[0]
            coins['LTC'] = f"${coin_price}"
    return coins


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def start(update, _):
    coin_keyboard = [["Bitcoin", "Ethereum"], ["Litecoin", "All coins"]]
    coin_markup = ReplyKeyboardMarkup(coin_keyboard, one_time_keyboard=True)
    update.message.reply_text('Используйте клавиатуру для ответа.\n'
                              'Команда /unset сбрасывает таймер.\n'
                              'Команда /now присылает курсы Bitcoin, Ethereum и Litecoin.\n'
                              'Команда /stop завершает работу.\n'
                              '\n'
                              '\n'
                              'Выберите криптовалюту', reply_markup=coin_markup)
    return 1


def now(update, context):
    price = get_coins_price()
    chat_id = update.message.chat_id
    message = f'BTC: {price["BTC"]}\n' \
              f'ETH: {price["ETH"]}\n' \
              f'LTC: {price["LTC"]}\n'
    context.bot.send_message(chat_id=chat_id, text=message)


def time(update, context):
    context.user_data['coin'] = update.message.text
    coin = context.user_data['coin']
    if coin in COINS:
        time_keyboard = [["24 часа", "12 часов"], ["1 час", "30 минут", '15 минут']]
        time_markup = ReplyKeyboardMarkup(time_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            "Выберите ответ с помощью клавиатуры либо введите сообщение в формате *цифра минут(час).\n"
            "Например: 3 часа.\n"
            '\n'
            '\n'
            'Выберите интервал между сообщениями.', reply_markup=time_markup)
        return 2
    else:
        coin_keyboard = [["Bitcoin", "Ethereum"], ["Litecoin", "All coins"]]
        coin_markup = ReplyKeyboardMarkup(coin_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            "Выберите криптовалюту", reply_markup=coin_markup)
        return 1


def set_timer(update, context):
    context.user_data['time'] = update.message.text
    data = context.user_data['time']
    if (data in TIME) or (' ' in data):
        data = data.split()
        if data[0].isdigit():
            chat_id = update.message.chat_id
            remove_job_if_exists(str(chat_id), context)
            if "час" in data[1]:
                timing = int(data[0]) * 60 * 60
                new_job = context.job_queue.run_repeating(task, interval=timing, first=1, name=str(chat_id),
                                                          context={'user_data': context.user_data,
                                                                   'chat_data': context.chat_data, "chat_id": chat_id})
                context.chat_data["job"] = new_job
            else:
                timing = int(data[0]) * 60
                new_job = context.job_queue.run_repeating(task, interval=timing, first=1, name=str(chat_id),
                                                          context={'user_data': context.user_data,
                                                                   'chat_data': context.chat_data, "chat_id": chat_id})
                context.chat_data["job"] = new_job
        else:
            time_keyboard = [["24 часа", "12 часов"], ["1 час", "30 минут", '15 минут']]
            time_markup = ReplyKeyboardMarkup(time_keyboard, one_time_keyboard=True)
            update.message.reply_text(
                "Выберите ответ с помощью клавиатуры либо введите сообщение в формате *цифра минут(час).\n"
                "Например: 3 часа.\n"
                '\n'
                '\n'
                'Выберите интервал между сообщениями.', reply_markup=time_markup)
            return 2
    else:
        time_keyboard = [["24 часа", "12 часов"], ["1 час", "30 минут", '15 минут']]
        time_markup = ReplyKeyboardMarkup(time_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            "Выберите ответ с помощью клавиатуры либо введите сообщение в формате *цифра минут(час).\n"
            "Например: 3 часа.\n"
            '\n'
            '\n'
            'Выберите интервал между сообщениями.',
            reply_markup=time_markup)
        return 2


def task(context):
    coin = context.job.context['user_data']['coin']
    price = get_coins_price()
    if coin != "All coins":
        if coin == 'Bitcoin':
            price = price["BTC"]
        elif coin == 'Litecoin':
            price = price["LTC"]
        elif coin == 'Ethereum':
            price = price['ETH']
        message = f'Курс {coin}: {price}'
        context.bot.send_message(chat_id=context.job.context['chat_id'], text=message)
    else:
        message = f'BTC: {price["BTC"]}\n' \
                  f'ETH: {price["ETH"]}\n' \
                  f'LTC: {price["LTC"]}\n'
        context.bot.send_message(chat_id=context.job.context['chat_id'], text=message)


def unset_timer(update, context):
    chat_id = update.message.chat_id
    if 'job' not in context.chat_data:
        update.message.reply_text('Нет активного таймера')
        return
    remove_job_if_exists(str(chat_id), context)
    time_keyboard = [["24 часа", "12 часов"], ["1 час", "30 минут", '15 минут']]
    time_markup = ReplyKeyboardMarkup(time_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Таймер снят", reply_markup=time_markup)
    return 2


def stop(update, context):
    update.message.reply_text('Завершаю работу')
    chat_id = update.message.chat_id
    if 'job' in context.chat_data:
        remove_job_if_exists(str(chat_id), context)
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN3, use_context=True)

    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [CommandHandler("stop", stop), MessageHandler(Filters.text, time)],
            2: [CommandHandler("stop", stop),
                CommandHandler("unset", unset_timer, pass_chat_data=True, pass_user_data=True),
                CommandHandler('now', now),
                MessageHandler(Filters.text, set_timer, pass_job_queue=True, pass_chat_data=True, pass_user_data=True)],
        },

        fallbacks=[CommandHandler("stop", stop)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
