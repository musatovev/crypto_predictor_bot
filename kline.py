class Kline:
    # 1576301400000 Open time
    # 0.00205460 Open
    # 0.00205480 High
    # 0.00205460 Low
    # 0.00205470 Close
    # 219.33000000 Volume
    # 1576301459999 Close time
    # 0.45065083 Quote asset volume
    # 5 Number of trades
    # 219.33000000 Taker buy base asset volume
    # 0.45065083 Taker buy quote asset volume
    # 0 Can be ignored
    def __repr__(self):
        return "Open time - " + str(self.time_open)  + "\n" +\
              "Open - " + str(self.price_open) + "\n" +\
              "High - " + str(self.price_high) + "\n" +\
              "Low - " + str(self.price_low) + "\n" +\
              "Close - " + str(self.price_close) + "\n" +\
              "Volume - " + str(self.volume) + "\n" +\
              "Close time - " + str(self.time_close) + "\n" +\
              "Quote asset volume - " + str(self.quote_asset_volume) + "\n" +\
              "Number of trades - " + str(self.number_of_trades) + "\n" +\
              "Taker buy base asset volume - " + str(self.taker_buy_base_asset_volume) + "\n" +\
              "Taker buy quote asset volume - " + str(self.taker_buy_quote_asset_volume)

    def __init__(self, mass):
        self.time_open = mass[0]
        self.price_open = mass[1]
        self.price_high = mass[2]
        self.price_low = mass[3]
        self.price_close = mass[4]
        self.volume = mass[5]
        self.time_close = mass[6]
        self.quote_asset_volume = mass[7]
        self.number_of_trades = mass[8]
        self.taker_buy_base_asset_volume = mass[9]
        self.taker_buy_quote_asset_volume = mass[10]