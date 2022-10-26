import backtrader as bt

from ibb.indicator.two_efforts import TwoEfforts


class BasicStrategy(bt.Strategy):
    def __init__(self, params=None):
        self.two_efforts = TwoEfforts(self.datas[0], params)

    def next(self):
        pass
