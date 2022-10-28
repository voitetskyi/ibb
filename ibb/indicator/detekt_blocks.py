import backtrader as bt

from ibb.indicator.tendency_indicator import TendencyIndicator


class Block:
    pass


class DetektBlocks(bt.Indicator):
    lines = ('zigzag',)
    plotinfo = dict(
        subplot=False,
        plotlinelabels=True,
        plotlinevalues=True,
        plotvaluetags=True,
    )
    plotlines = dict(zigzag=dict(_name='zigzag', color='red', ls='--', _skipnan=True),)

    def __init__(self, params=None):
        super(DetektBlocks, self).__init__()
        self.tendency_indicator = TendencyIndicator(self.data)
        self.tendency = self.tendency_indicator.tendency
        self.tendency_list = []
        self.blocks = []
        self.index = 0
        self.tendency_long = True if params is None else params['tendency_long']

    def detekt_blocks_index(self):
        self.index = len(self.data) - 1

    def atr(self):
        amount = 5
        n = 1 - amount
        s = 0
        for i in range(n, 1):
            s += self.data.high[i] - self.data.low[i]
        return (s / amount) * 0.2

    def add_tendency_point(self):
        if len(self.tendency) > 0 and self.tendency[0]['tendency_indicator_index'] == self.index:
            self.tendency_list.append(self.tendency.pop(0))
            if len(self.tendency_list) > 2:
                self.detekt_block()

    def add_block(self, high_price, low_price, block_type):
        block = Block()
        block.start_time = self.tendency_list[-2]['time']
        block.start_time_index = self.tendency_list[-2]['tendency_indicator_index']
        block.high_price = high_price
        block.end_time = self.tendency_list[-1]['time']
        block.end_time_index = self.tendency_list[-1]['tendency_indicator_index']
        block.low_price = low_price
        block.block_type = block_type
        self.blocks.append(block)

    def detekt_block(self):
        if self.tendency_long:
            if self.tendency_list[-2]['type'] == 'HH':
                if self.data.close[0] >= self.tendency_list[-3]['price'] + self.atr():
                    self.add_block(self.tendency_list[-2]['price'], self.tendency_list[-1]['price'], 'long')
                else:
                    self.tendency_long = False
                    self.blocks[-1].block_type = 'short_start'
        else:
            if self.tendency_list[-2]['type'] == 'LL':
                if self.data.close[0] <= self.tendency_list[-3]['price'] - self.atr():
                    self.add_block(self.tendency_list[-1]['price'], self.tendency_list[-2]['price'], 'short')
                else:
                    self.tendency_long = True
                    self.blocks[-1].block_type = 'long_start'

    def next(self):
        self.detekt_blocks_index()
        self.lines.zigzag[0] = self.tendency_indicator.lines.zigzag[0]
        self.add_tendency_point()

    @classmethod
    def plot(cls, figure, stat, plotter):
        blocks = stat[0].cerebro.runningstrats[0].detekt_blocks.blocks
        ax = figure[0].get_axes()[0]
        for t in blocks:
            if t.block_type == 'long':
                color = 'green'
            elif t.block_type == 'short':
                color = 'red'
            else:
                color = 'purple'
            xy = (t.start_time_index, t.low_price)
            width = t.end_time_index - t.start_time_index
            height = t.high_price - t.low_price
            ax.add_patch(plotter.mpyplot.Rectangle(xy, width, height, alpha=0.5, color=color))


if __name__ == '__main__':
    detekt_blocks = DetektBlocks()
