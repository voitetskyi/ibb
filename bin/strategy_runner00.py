import backtrader as bt
from datetime import datetime


class TendencyIndicator(bt.ind.PeriodN):
    lines = ('zigzag',)
    plotinfo = dict(
        subplot=False,
        plotlinelabels=True,
        plotlinevalues=True,
        plotvaluetags=True,
    )
    plotlines = dict(zigzag=dict(_name='zigzag', color='red', ls='--', _skipnan=True),)
    params = (('period', 2),)

    def __init__(self):
        super(TendencyIndicator, self).__init__()
        self.tendency = []

    def prenext(self):
        if self.data.open[0] < self.data.close:
            self.tendency.append({'time': self.data.datetime[0], 'price': self.data.low[0], 'type': 'MIN'})
        elif self.data.open[0] > self.data.close:
            self.tendency.append({'time': self.data.datetime[0], 'price': self.data.high[0], 'type': 'MAX'})
        else:
            if self.data.high - self.data.close > self.data.close - self.data.low:
                self.tendency.append({'time': self.data.datetime[0], 'price': self.data.high[0], 'type': 'MAX'})
            else:
                self.tendency.append({'time': self.data.datetime[0], 'price': self.data.low[0], 'type': 'MIN'})

    def next(self):
        if self.data.close[0] < self.data.close[-1] and self.tendency[-1]['type'] == 'MIN':
            if self.data.high[0] > self.data.high[-1]:
                self.zigzag[0] = self.data.high[0]
                self.tendency.append({'time': self.data.datetime[0], 'price': self.data.high[0], 'type': 'MAX'})
            else:
                self.zigzag[-1] = self.data.high[-1]
                self.tendency.append({'time': self.data.datetime[-1], 'price': self.data.high[-1], 'type': 'MAX'})
        elif self.data.close[0] > self.data.close[-1] and self.tendency[-1]['type'] == 'MAX':
            if self.data.low[0] < self.data.low[-1]:
                self.zigzag[0] = self.data.low[0]
                self.tendency.append({'time': self.data.datetime[0], 'price': self.data.low[0], 'type': 'MIN'})
            else:
                self.zigzag[-1] = self.data.low[-1]
                self.tendency.append({'time': self.data.datetime[-1], 'price': self.data.low[-1], 'type': 'MIN'})
        print(self.tendency)


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    cerebro = bt.Cerebro(stdstats=False)  # Инициируем "движок" BT, убираем стандартную статистику
    # cerebro.addobserver(bt.observers.Value)  # Отображаем кривую доходности
    cerebro.addobserver(bt.observers.BuySell, barplot=True, bardist=0.0001)  # Для небольшого временнОго интервала
                                                        # нужно уменьшить дистанцию от баров до маркеров входа/выхода
    # cerebro.addstrategy(Simple)  # Добавляем торговую систему
    cerebro.addindicator(TendencyIndicator)
    data = bt.feeds.GenericCSVData(
        dataname='../data/quotes_es.globex_1mm.csv',  # Файл для импорта
        separator=',',  # Колонки разделены табуляцией
        dtformat='%Y%m%d%H%M%S',  # Формат даты/времени DD.MM.YYYY HH:MI
        openinterest=-1,  # Открытого интереса в файле нет
        timeframe=bt.TimeFrame.Minutes,  # Для временнОго интервала отличного от дневок нужно его указать
        compression=1,  # Для миннутного интервала, отличного от 1, его нужно указать
        fromdate=datetime(2021, 1, 26, 0, 0),  # Начальная дата и время приема исторических данных (Входит)
        todate=datetime(2021, 1, 26, 1, 0))  # Конечная дата и время приема исторических данных (Не входит)
    cerebro.adddata(data)  # Привязываем исторические данные
    cerebro.broker.setcash(100000)  # Стартовый капитал для "бумажной" торговли
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)  # Кол-во в штуках для покупки/продажи
    cerebro.run()  # Запуск торговой системы
    cerebro.plot(style='bar')  # Рисуем график. Требуется matplotlib версии 3.2.2 (pip install matplotlib==3.2.2)
