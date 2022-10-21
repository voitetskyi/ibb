import backtrader as bt

from ibb.indicator.two_efforts import TwoEfforts


class BasicStrategy(bt.Strategy):
    def __init__(self):
        self.two_efforts = TwoEfforts(self.datas[0])

    def next(self):
        pass
