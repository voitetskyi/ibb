import backtrader as bt

from ibb.indicator.detekt_blocks import DetektBlocks


class BasicStrategy(bt.Strategy):
    def __init__(self, params=None):
        self.detekt_blocks = DetektBlocks(self.datas[0], params)

    def next(self):
        pass
