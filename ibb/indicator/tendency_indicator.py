import backtrader as bt


class TendencyIndicator(bt.Indicator):
    lines = ('zigzag',)
    plotinfo = dict(
        subplot=False,
        plotlinelabels=True,
        plotlinevalues=True,
        plotvaluetags=True,
    )
    plotlines = dict(zigzag=dict(_name='zigzag', color='red', ls='--', _skipnan=True),)

    def __init__(self):
        super(TendencyIndicator, self).__init__()
        self.tendency = []
        self.tendency_indicator_index = 0

    def get_time(self, index):
        return self.data.num2date(self.data.datetime[index])

    def append_tendency_point(self, index, type_of_point):
        price = self.data.high[index] if type_of_point == 'HH' else self.data.low[index]
        self.zigzag[index] = price
        self.tendency.append({'time': self.get_time(index), 'price': price, 'type': type_of_point,
                              'tendency_indicator_index': self.tendency_indicator_index})

    def first_point(self):
        if len(self.tendency) == 0:
            delta = self.data.open[0] - self.data.close[0]
            if delta < 0:
                self.append_tendency_point(0, 'LL')
            elif delta > 0:
                self.append_tendency_point(0, 'HH')
            else:
                if self.data.high[0] - self.data.close[0] > self.data.close[0] - self.data.low[0]:
                    self.append_tendency_point(0, 'HH')
                else:
                    self.append_tendency_point(0, 'LL')

    def next(self):
        if len(self.tendency) == 0:
            self.first_point()
        delta_close = self.data.close[0] - self.data.close[-1]
        local_maximum = max([self.data.high[-2], self.data.high[-1], self.data.high[0]])
        local_minimum = min([self.data.low[-2], self.data.low[-1], self.data.low[0]])
        type_min = self.tendency[-1]['type'] == 'LL'
        type_max = self.tendency[-1]['type'] == 'HH'
        if delta_close < 0 and type_min:
            index = 0 if self.data.high[0] > self.data.high[-1] else -1
            self.append_tendency_point(index, 'HH')
        if delta_close > 0 and type_max:
            index = 0 if self.data.low[0] < self.data.low[-1] else -1
            self.append_tendency_point(index, 'LL')
        if self.data.high[-1] == local_maximum and type_min:
            self.append_tendency_point(-1, 'HH')
        if self.data.low[-1] == local_minimum and type_max:
            self.append_tendency_point(-1, 'LL')
        self.tendency_indicator_index += 1


if __name__ == '__main__':
    tendency = TendencyIndicator()
