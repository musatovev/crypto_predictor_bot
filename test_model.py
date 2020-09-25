from datetime import datetime

import pandas
import requests
from tensorflow import keras
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException
from binance.websockets import BinanceSocketManager
from tensorflow_core.python.keras.models import model_from_json

from telegram.ext import Updater, CommandHandler

from main import norm

tg_key = '1306538615:AAF8HVkQz3iXhKO_kfsfl7D29kaai4U7bCA'
tg_id = '270341736'


client = Client("DIoZD2FRiut4Se5z36nSEStNoZybqdh5zjcz4UUBLt829YK4gU8jkeASRRxtoMhi",
                "vNTqYMsvtxJedku27kxkrjoGCC6LNaXRqAqly9Eg2r9iL3fyEM8s5uR9WYIw7r3d")

# get market depth
depth = client.get_order_book(symbol='BNBBTC')

# place a test market buy order, to place an actual order use the create_order function
order = client.create_test_order(
    symbol='BNBBTC',
    side=Client.SIDE_BUY,
    type=Client.ORDER_TYPE_MARKET,
    quantity=100)

# get all symbol prices
# prices = client.get_all_tickers()


PRICE_LESS = 0
PRICE_STABLE = 1
PRICE_RISE = 2

TRIGGER = 1


def prepare_data(klines):

    train_data, train_answers = [], []

    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore']

    all = pandas.DataFrame(klines, columns=columns)

    for x in range(len(all.values) - 19):

        price_open = list()
        price_high = list()
        price_low = list()
        price_close = list()
        volume = list()
        quote_asset_volume = list()
        number_of_trades = list()
        taker_buy_base_asset_volume = list()
        taker_buy_quote_asset_volume = list()

        for y in range(20):
            if y == 18:
                price_before = float(all['open'].get(x + y))

            if y == 19:
                price_after = float(all['close'].get(x + y))
                break

            price_open.append(float(all['open'].get(x + y)))
            price_high.append(float(all['high'].get(x + y)))
            price_low.append(float(all['low'].get(x + y)))
            price_close.append(float(all['close'].get(x + y)))
            volume.append(float(all['volume'].get(x + y)))
            quote_asset_volume.append(float(all['quote_av'].get(x + y)))
            number_of_trades.append(float(all['trades'].get(x + y)))
            taker_buy_base_asset_volume.append(float(all['tb_base_av'].get(x + y)))
            taker_buy_quote_asset_volume.append(float(all['tb_quote_av'].get(x + y)))

        layer = list()
        layer.append(norm(price_open))
        layer.append(norm(price_high))
        layer.append(norm(price_low))
        layer.append(norm(price_close))
        layer.append(norm(volume))
        layer.append(norm(quote_asset_volume))
        layer.append(norm(number_of_trades))
        layer.append(norm(taker_buy_base_asset_volume))
        layer.append(norm(taker_buy_quote_asset_volume))

        if price_before >= price_after:
            # Цена ПОСЛЕ меньше на TRIGGER процентов
            answer = PRICE_LESS

            # Различие между ценой не более TRIGGER процентов
            if (100 - price_after / price_before * 100) < TRIGGER:
                answer = PRICE_STABLE

        else:
            # Цена ПОСЛЕ больше на TRIGGER процентов
            answer = PRICE_RISE

            # Различие между ценой не более TRIGGER процентов
            if (100 - price_before / price_after * 100) < TRIGGER:
                answer = PRICE_STABLE

            train_data.append(layer)
            train_answers.append(answer)

    return train_data




if __name__ == '__main__':

    data = client.get_historical_klines("BNBBTC", Client.KLINE_INTERVAL_1HOUR, "24 hours ago UTC")
    data = data[20 - len(data):]

    predict_data = prepare_data(data)

    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("model.h5")
    result = loaded_model.predict(predict_data)

    msg = str()

    if (list(result[0]).index(max(result[0]))) == 2:
        msg += 'Время открытия - ' + str(datetime.fromtimestamp(data[-1][0]/1000)) + '\n'
        msg += 'Цена открытия - ' + data[-1][1] + '\n'
        msg += '-------------------------------\n'
        msg += 'Время закрытия - ' + str(datetime.fromtimestamp(data[-1][0] / 1000 + 3600*2)) + '\n'
        msg += 'Ожидаемая цена - ' + (str(float(data[-1][1]) / 100 + float(data[-1][1])))
    else:
        msg += 'Цена не вырастет в ближайшие два часа'

    send_text = 'https://api.telegram.org/bot' + tg_key + '/sendMessage?chat_id=' + tg_id + '&parse_mode=Markdown&text=' + msg
    rec = requests.get(send_text)
    print(msg)