from datetime import datetime

import backtrader as bt

from backtrader.plot import Plot_OldSync

from ibb.indicator.two_efforts import TwoEfforts
from ibb.strategy.basic_strategy import BasicStrategy


if __name__ == '__main__':
    cerebro = bt.Cerebro(stdstats=False)
    # cerebro.addobserver(bt.observers.Value)
    cerebro.addobserver(bt.observers.BuySell, barplot=True, bardist=0.0001)
    cerebro.addstrategy(BasicStrategy)
    # cerebro.addindicator(TwoEfforts)
    data = bt.feeds.GenericCSVData(
        dataname='../data/quotes_es.globex_1mm.csv',
        separator=',',
        dtformat='%Y%m%d%H%M%S',
        openinterest=-1,
        timeframe=bt.TimeFrame.Minutes,
        compression=1,
        fromdate=datetime(2021, 1, 26, 0, 0),
        todate=datetime(2021, 1, 26, 4, 0))
    cerebro.adddata(data)
    cerebro.broker.setcash(100000)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)
    stat = cerebro.run()

    plotter = Plot_OldSync(style='bar', bardown='grey', volume=False)
    figure = plotter.plot(cerebro.runstrats[0][0], figid=0 * 100)
    TwoEfforts.plot(figure, stat, plotter)

    plotter.show()
