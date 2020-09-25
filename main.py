import csv
import os
import random
import sys
from datetime import datetime

import numpy
import pandas
from tensorflow import keras

from kline import Kline


PRICE_LESS = 0
PRICE_STABLE = 1
PRICE_RISE = 2

TRIGGER = 1

def norm(mass):
    minimum = min(mass)
    maximum = max(mass)
    try:
        return [(el - minimum) / (maximum - minimum) for el in mass]
    except ZeroDivisionError:
        return [0 for el in mass]


def select_only_rise_predict(all_data, all_answers):
    if len(all_data) != len(all_answers):
        raise Exception("length data not equal length answers")

    rise_data, rise_answers = list(), list()
    data, answers = all_data, all_answers

    for i in range(len(all_data)):
        if all_answers[0] == PRICE_RISE:
            rise_data.append(all_data.pop(0))
            rise_answers.append(all_answers.pop(0))
        else:
            data.append(all_data.pop(0))
            answers.append(all_answers.pop(0))
    return rise_data, rise_answers, data, answers


def get_data(files):

    train_data = []
    train_answers = []

    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore']

    all = []

    for file in files:
        all.append(pandas.read_csv(file, delimiter=',', usecols=columns))

    all = pandas.concat(all, axis=0, ignore_index=True)
    price_before = float()
    price_after = float()

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

    return train_data, train_answers


def evaluate_predict(model, data, answers):
    test_loss, test_acc = model.evaluate(data, answers, verbose=1)

    print('Точность на проверочных данных:', test_acc, '\n')

    predictions = model.predict(all_data)

    rise_predicts = 0
    stable_predict = 0
    less_predict = 0

    correct_positive_predicts = 0
    correct_stable_predict = 0
    correct_less_predict = 0

    print('Всего предсказаний - ' + str(len(predictions)))
    for i in range(len(predictions)):
        predict = list(predictions[i]).index(max(predictions[i]))
        # if predict == PRICE_RISE:
        if predict == PRICE_RISE and predictions[i][PRICE_RISE] > 1:
            rise_predicts += 1
            if predict == all_answers[i]:
                # print(predictions[i][PRICE_RISE])
                correct_positive_predicts += 1
        elif predict == PRICE_STABLE:
            stable_predict += 1
            if predict == all_answers[i]:
                correct_stable_predict += 1
        elif predict == PRICE_LESS:
            less_predict += 1
            if predict == all_answers[i]:
                correct_less_predict += 1

    print('\n\nВсего предсказаний роста курса - ' + str(rise_predicts))
    print('Из них успешных предсказаний - ' + str(correct_positive_predicts))
    if rise_predicts != 0:
        percent = 100 / rise_predicts * correct_positive_predicts
        print('Точность предсказания - ' + str(percent))
        if percent > 70:
            model_json = model.to_json()
            with open("model.json", "w") as json_file:
                json_file.write(model_json)
            model.save_weights("model.h5")
            print("Saved model to disk")
            sys.exit(0)
    else:
        print('Точность предсказания - 0')

    print('\nВсего предсказаний стабильности курса - ' + str(stable_predict))
    print('Из них успешных предсказаний - ' + str(correct_stable_predict))
    if stable_predict != 0:
        print('Точность предсказания - ' + str((100 / stable_predict * correct_stable_predict)))
    else:
        print('Точность предсказания - 0')

    print('\nВсего предсказаний падения курса - ' + str(less_predict))
    print('Из них успешных предсказаний - ' + str(correct_less_predict))
    if less_predict != 0:
        print('Точность предсказания - ' + str((100 / less_predict * correct_less_predict)))
    else:
        print('Точность предсказания - 0')

    return rise_predicts

if __name__ == '__main__':
    # get_all_binance('ETHBTC', '1d', True)
    # get_all_binance('ADABTC', '1d', True)
    # get_all_binance('ZILBTC', '1d', True)
    # get_all_binance('XLMBTC', '1d', True)
    # get_all_binance('LINKBTC', '1d', True)
    # get_all_binance('BCHBTC', '1d', True)
    # get_all_binance('VETBTC', '1d', True)
    # get_all_binance('XRPBTC', '1d', True)
    # get_all_binance('NEOBTC', '1d', True)
    # get_all_binance('LTCBTC', '1d', True)
    # get_all_binance('EOSBTC', '1d', True)
    # get_all_binance('MATICBTC', '1d', True)
    # get_all_binance('XTZBTC', '1d', True)
    # get_all_binance('TRXBTC', '1d', True)
    # get_all_binance('ERDBTC', '1d', True)
    # get_all_binance('XMRBTC', '1d', True)

    all_data, all_answers = get_data(['ETHBTC-1d-data.csv'])
                                      # 'ADABTC-1d-data.csv',
                                      # 'ZILBTC-1d-data.csv',
                                      # 'XLMBTC-1d-data.csv',
                                      # 'LINKBTC-1h-data.csv',
                                      # 'BCHBTC-1h-data.csv',
                                      # 'VETBTC-1h-data.csv',
                                      # 'XRPBTC-1h-data.csv',
                                      # 'NEOBTC-1h-data.csv',
                                      # 'LTCBTC-1h-data.csv',
                                      # 'EOSBTC-1h-data.csv',
                                      # 'MATICBTC-1h-data.csv',
                                      # 'XTZBTC-1h-data.csv',
                                      # 'TRXBTC-1h-data.csv',
                                      # 'ERDBTC-1h-data.csv',
                                      # 'XMRBTC-1h-data.csv'])

    test_data, test_answers = all_data[int(len(all_data) / 1.1):], all_answers[int(len(all_answers) / 1.1):]
    train_data, train_answers = all_data[:int(len(all_data) / 1.1)], all_answers[:int(len(all_answers) / 1.1)]

    rise_predicts = 0

    while rise_predicts < 70:
        model = keras.Sequential()
        model.add(keras.layers.Flatten(input_shape=(9, 19)))
        model.add(keras.layers.Dense(1024, activation='linear'))
        model.add(keras.layers.Dense(512, activation='linear'))
        model.add(keras.layers.Dense(256, activation='linear'))
        model.add(keras.layers.Dense(3, activation='linear'))

        model.compile(optimizer='adam',
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])

        model.fit(train_data, train_answers, epochs=1, batch_size=1, verbose=1)
        rise_predicts = evaluate_predict(model, test_data, test_answers)

