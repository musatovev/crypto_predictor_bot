import csv

from tensorflow import keras

from kline import Kline


PRICE_LESS = 0
PRICE_STABLE = 1
PRICE_RISE = 2

TRIGGER = 1


def get_data(files):
    klines = list()
    train_data = []
    train_answers = []

    for file in files:
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    klines.append(Kline(row))
                    line_count += 1

        price_before = float()
        price_after = float()

        for x in range(len(klines) - 9):
            layer = []
            for y in range(10):
                if y == 8:
                    price_before = float(klines[x + y].price_open)

                if y == 9:
                    price_after = float(klines[x + y].price_close)
                    break

                layer.append(float(klines[x + y].price_open))
                layer.append(float(klines[x + y].price_high))
                layer.append(float(klines[x + y].price_low))
                layer.append(float(klines[x + y].price_close))
                layer.append(float(klines[x + y].volume) / 100000)
                layer.append(float(klines[x + y].quote_asset_volume) / 100000)
                layer.append(float(klines[x + y].number_of_trades) / 1000000)
                layer.append(float(klines[x + y].taker_buy_base_asset_volume) / 100000)
                layer.append(float(klines[x + y].taker_buy_quote_asset_volume) / 100000)

            train_data.append(layer)

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

            train_answers.append(answer)

    return train_data, train_answers


if __name__ == '__main__':

    all_data, all_answers = get_data(['ETHBTC-1h-data.csv',
                                      'ADABTC-1h-data.csv',
                                      'ZILBTC-1h-data.csv',
                                      'XLMBTC-1h-data.csv',
                                      'LINKBTC-1h-data.csv',
                                      'BCHBTC-1h-data.csv',
                                      'VETBTC-1h-data.csv',
                                      'XRPBTC-1h-data.csv',
                                      'NEOBTC-1h-data.csv',
                                      'LTCBTC-1h-data.csv',
                                      'EOSBTC-1h-data.csv',
                                      'MATICBTC-1h-data.csv',
                                      'XTZBTC-1h-data.csv',
                                      'TRXBTC-1h-data.csv',
                                      'ERDBTC-1h-data.csv',
                                      'XMRBTC-1h-data.csv'])

    test_data, test_answers = all_data[int(len(all_data) / 1.1):], all_answers[int(len(all_answers) / 1.1):]
    train_data, train_answers = all_data[:int(len(all_data) / 1.1)], all_answers[:int(len(all_answers) / 1.1)]

    model = keras.Sequential()
    model.add(keras.layers.Flatten(input_shape=(81,)))
    model.add(keras.layers.Dense(1024, activation='linear'))
    model.add(keras.layers.Dense(512, activation='linear'))
    model.add(keras.layers.Dense(256, activation='linear'))
    model.add(keras.layers.Dense(3, activation='linear'))

    model.compile(optimizer='rmsprop',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    model.fit(train_data, train_answers, epochs=1, batch_size=2, verbose=1)

    test_loss, test_acc = model.evaluate(test_data, test_answers, verbose=1)

    print('Точность на проверочных данных:', test_acc, '\n')

    predictions = model.predict(test_data)

    rise_predicts = 0
    stable_predict = 0
    less_predict = 0

    correct_positive_predicts = 0
    correct_stable_predict = 0
    correct_less_predict = 0

    print('Всего предсказаний - ' + str(len(predictions)))
    for i in range(len(predictions)):
        predict = list(predictions[i]).index(max(predictions[i]))
        if predict == PRICE_RISE:
            rise_predicts += 1
            if predict == test_answers[i]:
                correct_positive_predicts += 1
        elif predict == PRICE_STABLE:
            stable_predict += 1
            if predict == test_answers[i]:
                correct_stable_predict += 1
        elif predict == PRICE_LESS:
            less_predict += 1
            if predict == test_answers[i]:
                correct_less_predict += 1

    print('Всего предсказаний роста курса - ' + str(rise_predicts))
    print('Из них успешных предсказаний - ' + str(correct_positive_predicts))
    if rise_predicts != 0:
        print('Точность предсказания - ' + str((100 / rise_predicts * correct_positive_predicts)))
    else:
        print('Точность предсказания - 0')

    print('\n\nВсего предсказаний стабильности курса - ' + str(stable_predict))
    print('Из них успешных предсказаний - ' + str(correct_stable_predict))
    if stable_predict != 0:
        print('Точность предсказания - ' + str((100 / stable_predict * correct_stable_predict)))
    else:
        print('Точность предсказания - 0')

    print('\n\nВсего предсказаний падения курса - ' + str(less_predict))
    print('Из них успешных предсказаний - ' + str(correct_less_predict))
    if less_predict != 0:
        print('Точность предсказания - ' + str((100 / less_predict * correct_less_predict)))
    else:
        print('Точность предсказания - 0')
