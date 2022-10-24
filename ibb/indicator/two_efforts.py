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
        self.tendency_list = []
        self.zones = []
        self.index = 0
        self.status = 0

    def two_efforts_index(self):
        self.index = len(self.data) - 1

    def add_tendency_point(self):
        if len(self.tendency) > 0 and self.tendency[0]['tendency_indicator_index'] == self.index:
            self.tendency_list.append(self.tendency.pop(0))

    def get_time(self, index):
        return self.data.num2date(self.data.datetime[index])

    def add_zone(self, start_time, start_time_index, start_price, end_time, end_time_index, end_price, zone_type):
        self.zones.append({'start_time': start_time, 'start_time_index': start_time_index, 'start_price': start_price,
                           'end_time': end_time, 'end_time_index': end_time_index, 'end_price': end_price,
                           'zone_type': zone_type})
        print(self.zones[-1])

    def short_or_long(self):
        if self.tendency_list[-4]['type'] == 'LL':
            if self.tendency_list[-4]['price'] < self.tendency_list[-2]['price']\
                    and self.tendency_list[-3]['price'] < self.tendency_list[-1]['price']:
                self.status = 'LONG'
        if self.tendency_list[-4]['type'] == 'HH':
            if self.tendency_list[-4]['price'] > self.tendency_list[-2]['price']\
                    and self.tendency_list[-3]['price'] > self.tendency_list[-1]['price']:
                self.status = 'SHORT'

    def two_efforts(self):
        if self.tendency_list[-1]['type'] == 'LL':
            if self.data.close[0] > self.tendency_list[-2]['price']:
                zone_type = 'two_imp' if self.status == 'SHORT' else 'tendency_win'
                self.add_zone(self.tendency_list[-2]['time'], self.tendency_list[-3]['tendency_indicator_index'],
                              self.tendency_list[-1]['price'], self.get_time(0), self.index,
                              self.tendency_list[-2]['price'], zone_type)
        if self.tendency_list[-1]['type'] == 'HH':
            if self.data.close[0] < self.tendency_list[-2]['price']:
                zone_type = 'two_imp' if self.status == 'LONG' else 'tendency_win'
                self.add_zone(self.tendency_list[-2]['time'], self.tendency_list[-3]['tendency_indicator_index'],
                              self.tendency_list[-1]['price'], self.get_time(0), self.index,
                              self.tendency_list[-2]['price'], zone_type)

    def next(self):
        self.two_efforts_index()
        self.add_tendency_point()
        self.lines.zigzag[0] = self.tendency_indicator.lines.zigzag[0]
        if len(self.tendency_list) > 3:
            self.short_or_long()
        if self.status != 0:
            self.two_efforts()
        print(self.index, self.status)

    @classmethod
    def plot(cls, figure, stat, plotter):
        zones = stat[0].cerebro.runningstrats[0].two_efforts.zones
        ax = figure[0].get_axes()[0]
        for t in zones:
            xy = (t['start_time_index'], t['start_price'])
            width = t['end_time_index'] - t['start_time_index']
            height = t['end_price'] - t['start_price']
            ax.add_patch(plotter.mpyplot.Rectangle(xy, width, height, alpha=0.25, color='red'))


if __name__ == '__main__':
    two_efforts = TwoEfforts()
