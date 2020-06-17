import csv

import pygame
from pygame.draw import line
from tensorflow import keras

from kline import Kline


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
                mass = 0

                # Различие между ценой не более TRIGGER процентов
                if (100 - price_after / price_before * 100) < TRIGGER:
                    mass = 1

            else:
                # Цена ПОСЛЕ больше на TRIGGER процентов
                mass = 2

                # Различие между ценой не более TRIGGER процентов
                if (100 - price_before / price_after * 100) < TRIGGER:
                    mass = 1

            train_answers.append(mass)

    return train_data, train_answers


if __name__ == '__main__':

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (125, 125, 125)
    LIGHT_BLUE = (64, 128, 255)
    GREEN = (0, 200, 64)
    RED = (255, 0, 0)
    YELLOW = (225, 225, 0)
    PINK = (230, 50, 230)

    TRIGGER = 1
    WIDTH = 500
    HEIGHT = 400

    all_data, all_answers = get_data(['ETHBTC-1h-data.csv'])
    test_data, test_answers = all_data[int(len(all_data) / 1.1):], all_answers[int(len(all_answers) / 1.1):]
    train_data, train_answers = all_data[:int(len(all_data) / 1.1)], all_answers[:int(len(all_answers) / 1.1)]

    # model = keras.Sequential()
    # model.add(keras.layers.Flatten(input_shape=(81,)))
    # model.add(keras.layers.Dense(512, activation='linear'))
    # model.add(keras.layers.Dense(1024, activation='linear'))
    # model.add(keras.layers.Dense(256, activation='linear'))
    # model.add(keras.layers.Dense(3, activation='linear'))

    # model.compile(optimizer='rmsprop',
    #               loss='sparse_categorical_crossentropy',
    #               metrics=['accuracy'])
    #
    # model.fit(train_data, train_answers, epochs=1, batch_size=10, verbose=1)
    #
    # test_loss, test_acc = model.evaluate(test_data, test_answers, verbose=1)
    #
    # print('Точность на проверочных данных:', test_acc, '\n')
    #
    # predictions = model.predict(test_data)

    pygame.init()



    sc = pygame.display.set_mode((WIDTH, HEIGHT))
    graphic = 0
    while True:
        y = 3
        coord_x = 10
        previous_y = int()
        previous_x = int()
        coord_y_for_predict = int()
        previous_y_for_predict = int()

        y = 1
        mass = list()
        while y < len(test_data[graphic]):
            mass.append(test_data[graphic][y])
            y += 9

        print(mass)
        print(max(mass))
        maximum = max(mass)
        minimum = min(mass)
        mass = [(el - minimum) * ((HEIGHT/2) / (maximum - minimum)) + (HEIGHT / 4) for el in mass]
        print(mass)
        y = 0
        while y < len(mass):

            # coord_y = HEIGHT - test_data[graphic][y] * 200000 % 1000
            # coord_y_for_predict = coord_y - HEIGHT / 2

            if y > 0:
                # pygame.draw.line(sc, WHITE, (previous_x, previous_y_for_predict), (coord_x, coord_y_for_predict), 2)
                pygame.draw.line(sc, WHITE, (previous_x, previous_y), (coord_x, mass[y]), 2)

            previous_y = mass[y]
            previous_x = coord_x
            previous_y_for_predict = coord_y_for_predict

            y += 1
            coord_x += 30


        # while index_y < len(test_data[graphic]):
        #
        #     coord_y = HEIGHT - test_data[graphic][index_y] * 200000 % 1000
        #     coord_y_for_predict = coord_y - HEIGHT / 2
        #
        #     if index_y > 0:
        #         pygame.draw.line(sc, WHITE, (previous_x, previous_y_for_predict), (coord_x, coord_y_for_predict), 2)
        #         pygame.draw.line(sc, WHITE, (previous_x, previous_y), (coord_x, coord_y), 2)
        #
        #     previous_y = coord_y
        #     previous_x = coord_x
        #     previous_y_for_predict = coord_y_for_predict
        #
        #     index_y += 9
        #     coord_x += 30

        answer_y = previous_y
        COLOR = LIGHT_BLUE
        if train_answers[graphic] < 1:
            # вверх
            answer_y -= 30
            COLOR = GREEN
        elif train_answers[graphic] > 1:
            # вниз
            answer_y += 30
            COLOR = RED

        # predict_y = previous_y_for_predict
        # COLOR_PREDICT = LIGHT_BLUE
        # if list(predictions[graphic]).index(max(predictions[graphic])) > 1:
        #     predict_y -= 30
        #     COLOR_PREDICT = GREEN
        # elif list(predictions[graphic]).index(max(predictions[graphic])) < 1:
        #     predict_y += 30
        #     COLOR_PREDICT = RED

        # pygame.draw.line(sc, COLOR_PREDICT, (previous_x, previous_y_for_predict), (coord_x + 50, predict_y), 2)
        pygame.draw.line(sc, COLOR, (previous_x, previous_y), (coord_x + 50, answer_y), 2)

        pygame.display.update()
        update = True
        while update:
            pygame.time.delay(10)
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    exit()
                elif i.type == pygame.KEYDOWN:
                    if i.key == pygame.K_RIGHT:
                        graphic += 1
                        update = False
                        sc.fill(BLACK)
                    elif i.key == pygame.K_LEFT:
                        graphic -= 1
                        update = False
                        sc.fill(BLACK)