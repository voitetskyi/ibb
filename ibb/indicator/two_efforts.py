import backtrader as bt

from ibb.indicator.tendency_indicator import TendencyIndicator


class Block:
    def __init__(self):
        self.flag = 0


class TwoEfforts(bt.Indicator):
    lines = ('zigzag', 'up', 'down',)
    plotinfo = dict(
        subplot=False,
        plotlinelabels=True,
        plotlinevalues=True,
        plotvaluetags=True,
    )
    plotlines = dict(zigzag=dict(_name='zigzag', color='red', ls='--', _skipnan=True),
                     up=dict(_name='up', color='green', marker='^', fillstyle='full'),
                     down=dict(_name='down', color='red', marker='v', fillstyle='full'),)

    def __init__(self, params=None):
        super(TwoEfforts, self).__init__()
        self.tendency_indicator = TendencyIndicator(self.data)
        self.tendency = self.tendency_indicator.tendency
        self.tendency_list = []
        self.blocks = []
        self.index = 0
        self.tendency_long = True if params is None else params['tendency_long']

    def two_efforts_index(self):
        self.index = len(self.data) - 1

    def add_tendency_point(self):
        if len(self.tendency) > 0 and self.tendency[0]['tendency_indicator_index'] == self.index:
            self.tendency_list.append(self.tendency.pop(0))

    def get_time(self, index):
        return self.data.num2date(self.data.datetime[index])

    def add_block(self, end_price, block_type):
        block = Block()
        block.start_time = self.tendency_list[-3]['time']
        block.start_time_index = self.tendency_list[-3]['tendency_indicator_index']
        block.start_price = self.tendency_list[-2]['price']
        block.end_time = self.tendency_list[-2]['time']
        block.end_time_index = self.tendency_list[-2]['tendency_indicator_index']
        block.end_price = end_price
        block.block_type = block_type
        self.blocks.append(block)

    def short_or_long(self):
        if self.tendency_list[-4]['type'] == 'LL':
            if self.tendency_list[-4]['price'] < self.tendency_list[-2]['price']\
                    and self.tendency_list[-3]['price'] < self.tendency_list[-1]['price']:
                self.tendency_long = True
        if self.tendency_list[-4]['type'] == 'HH':
            if self.tendency_list[-4]['price'] > self.tendency_list[-2]['price']\
                    and self.tendency_list[-3]['price'] > self.tendency_list[-1]['price']:
                self.tendency_long = False

    def detekt_blocks(self):
        if (self.index - 1) == self.tendency_list[-1]['tendency_indicator_index']:
            if self.tendency_long and self.tendency_list[-1]['type'] == 'HH':
                if self.tendency_list[-3]['price'] < self.tendency_list[-1]['price']:
                    end_price = self.tendency_list[-3]['price']
                else:
                    end_price = self.tendency_list[-1]['price']
                self.add_block(end_price, 'LONG')
            if not self.tendency_long and self.tendency_list[-1]['type'] == 'LL':
                if self.tendency_list[-3]['price'] > self.tendency_list[-1]['price']:
                    end_price = self.tendency_list[-3]['price']
                else:
                    end_price = self.tendency_list[-1]['price']
                self.add_block(end_price, 'SHORT')

    def block_exit(self):
        if self.blocks[-1].block_type == 'LONG':
            if self.data.close[0] > self.blocks[-1].end_price:
                self.blocks[-1].flag = 'UP'
                self.lines.up[0] = self.data.close[0]
            if self.data.close[0] < self.blocks[-1].start_price:
                self.blocks[-1].flag = 'DOWN'
                self.lines.down[0] = self.data.close[0]
        if self.blocks[-1].block_type == 'SHORT':
            if self.data.close[0] > self.blocks[-1].start_price:
                self.blocks[-1].flag = 'UP'
                self.lines.up[0] = self.data.close[0]
            if self.data.close[0] < self.blocks[-1].end_price:
                self.blocks[-1].flag = 'DOWN'
                self.lines.down[0] = self.data.close[0]
        # print(self.index, self.blocks[-1].flag)

    def next(self):
        self.two_efforts_index()
        self.lines.zigzag[0] = self.tendency_indicator.lines.zigzag[0]
        if len(self.tendency_list) > 3:
            self.short_or_long()
        if len(self.tendency_list) > 3:
            self.detekt_blocks()
        if len(self.blocks) > 0:
            self.block_exit()
        self.add_tendency_point()

    @classmethod
    def plot(cls, figure, stat, plotter):
        zones = stat[0].cerebro.runningstrats[0].two_efforts.blocks
        ax = figure[0].get_axes()[0]
        for t in zones:
            color = 'green' if t.block_type == 'LONG' else 'red'
            xy = (t.start_time_index, t.start_price)
            width = t.end_time_index - t.start_time_index
            height = t.end_price - t.start_price
            ax.add_patch(plotter.mpyplot.Rectangle(xy, width, height, alpha=0.5, color=color))


if __name__ == '__main__':
    two_efforts = TwoEfforts()
