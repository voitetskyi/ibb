import backtrader as bt

from ibb.indicator.tendency_indicator import TendencyIndicator


class TwoEfforts(bt.Indicator):
    lines = ('zigzag',)
    plotinfo = dict(
        subplot=False,
        plotlinelabels=True,
        plotlinevalues=True,
        plotvaluetags=True,
    )
    plotlines = dict(zigzag=dict(_name='zigzag', color='red', ls='--', _skipnan=True),)

    def __init__(self):
        super(TwoEfforts, self).__init__()
        self.tendency_indicator = TendencyIndicator(self.data)
        self.tendency = self.tendency_indicator.tendency
        self.zones = []
        self.status = 0
        self.two_efforts_index = 0

    def get_time(self, index):
        return self.data.num2date(self.data.datetime[index])

    def add_zone(self, start_time, start_time_index, start_price, end_time, end_time_index, end_price, zone_type):
        self.zones.append({'start_time': start_time, 'start_time_index': start_time_index, 'start_price': start_price,
                           'end_time': end_time, 'end_time_index': end_time_index, 'end_price': end_price,
                           'zone_type': zone_type})

    def short_or_long(self):
        if self.tendency[-4]['type'] == 'LL':
            if self.tendency[-4]['price'] < self.tendency[-2]['price']\
                    and self.tendency[-3]['price'] < self.tendency[-1]['price']:
                self.status = 'SHORT'
            if self.tendency[-4]['type'] == 'HH':
                if self.tendency[-4]['price'] > self.tendency[-2]['price']\
                        and self.tendency[-3]['price'] > self.tendency[-1]['price']:
                    self.status = 'LONG'

    def two_efforts(self):
        if self.tendency[-1]['type'] == 'LL':
            if self.data.close[0] > self.tendency[-2]['price']:
                zone_type = 'two_imp' if self.status == 'SHORT' else 'tendency_win'
                self.add_zone(self.tendency[-3]['time'], self.tendency[-3]['tendency_indicator_index'],
                              self.tendency[-1]['price'], self.get_time(0), self.two_efforts_index,
                              self.tendency[-2]['price'], zone_type)
        if self.tendency[-1]['type'] == 'HH':
            if self.data.close[0] < self.tendency[-2]['price']:
                zone_type = 'two_imp' if self.status == 'LONG' else 'tendency_win'
                self.add_zone(self.tendency[-3]['time'], self.tendency[-3]['tendency_indicator_index'],
                              self.tendency[-1]['price'], self.get_time(0), self.two_efforts_index,
                              self.tendency[-2]['price'], zone_type)

    def next(self):
        self.lines.zigzag[0] = self.tendency_indicator.lines.zigzag[0]
        if self.status == 0 and len(self.tendency) > 4:
            self.short_or_long()
        if self.status != 0:
            self.two_efforts()
        self.two_efforts_index += 1
        if self.two_efforts_index == 121:
            print('zones:', self.zones)
        print(len(self.data))

    @classmethod
    def plot(cls, figure, stat):
        print(type(figure[0]), figure[0])
        # zones = stat[0].cerebro.runningstrats[0].two_efforts.zones
        # ax = figure[0].get_axes()[0]
        # for t in zones:
        #     xy = (0, cerebro.datas[0].close[-20])
        #     width = 1 - 0
        #     height = cerebro.datas[0].close[0] - cerebro.datas[0].close[-10]
        #     ax.add_patch(plotter.mpyplot.Rectangle((0, 3820), 5, 5000))


if __name__ == '__main__':
    two_efforts = TwoEfforts()
