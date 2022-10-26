from unittest import TestCase
import backtrader as bt
import pandas as pd

from ibb.strategy.basic_strategy import BasicStrategy
from ibb.util.quote_builder import str_to_quote


class TwoEffortsTest(TestCase):

    def test_should_detekt_simple_long_block(self):
        quotes = """
                 |...9
           |   |
         |   |
        |
        """
        zones = run_two_efforts_strategy(quotes, {'tendency_long': True})
        self.assertEqual(1, len(zones))

    def test_should_not_detekt_simple_long_block(self):
        quotes = """
             |
           |   |   |
         |       |   |
        |              |
        """
        zones = run_two_efforts_strategy(quotes, {'tendency_long': True})
        self.assertEqual(0, len(zones))

    def test_should_detekt_simple_short_block(self):
        quotes = """
        |
          |   |
            |   |...1
                  |
        """
        zones = run_two_efforts_strategy(quotes, {'tendency_long': False})
        self.assertEqual(1, len(zones))

    def test_should_not_detekt_simple_short_block(self):
        quotes = """
        |           |
          |   |   |
            |   |
        """
        zones = run_two_efforts_strategy(quotes, {'tendency_long': False})
        self.assertEqual(0, len(zones))


def run_two_efforts_strategy(quotes, params):
    q = pd.DataFrame(str_to_quote(quotes))
    q['datetime'] = pd.to_datetime(q['datetime'])
    q['volume'] = 0
    q = q.set_index('datetime')
    data = bt.feeds.PandasData(dataname=q)
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.adddata(data)
    cerebro.addstrategy(BasicStrategy, params)
    stat = cerebro.run()
    return stat[0].cerebro.runningstrats[0].two_efforts.zones
