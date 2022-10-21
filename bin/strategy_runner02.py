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

    def get_time(self, index):
        return self.data.num2date(self.data.datetime[index])

    def append_tendency_point(self, index, type_of_point):
        price = self.data.high[index] if type_of_point == 'HH' else self.data.low[index]
        self.zigzag[index] = price
        self.tendency.append({'time': self.get_time(index), 'price': price, 'type': type_of_point})

    def prenext(self):
        if len(self.tendency) == 0:
            delta = self.data.open[0] - self.data.close[0]
            if delta < 0:
                self.append_tendency_point(0, 'LL')
            elif delta > 0:
                self.append_tendency_point(0, 'HH')
            else:
                if self.data.high[0] - self.data.close[0] > self.data.close[0] - self.data.low[0]:
                    self.append_tendency_point(0, 'HH')
                else:
                    self.append_tendency_point(0, 'LL')
            print(self.tendency)

    def next(self):
        delta_close = self.data.close[0] - self.data.close[-1]
        local_maximum = max([self.data.high[-2], self.data.high[-1], self.data.high[0]])
        local_minimum = min([self.data.low[-2], self.data.low[-1], self.data.low[0]])
        type_min = self.tendency[-1]['type'] == 'LL'
        type_max = self.tendency[-1]['type'] == 'HH'
        if delta_close < 0 and type_min:
            index = 0 if self.data.high[0] > self.data.high[-1] else -1
            self.append_tendency_point(index, 'HH')
        if delta_close > 0 and type_max:
            index = 0 if self.data.low[0] < self.data.low[-1] else -1
            self.append_tendency_point(index, 'LL')
        if self.data.high[-1] == local_maximum and type_min:
            self.append_tendency_point(-1, 'HH')
        if self.data.low[-1] == local_minimum and type_max:
            self.append_tendency_point(-1, 'LL')
        # print(self.get_time(-1))
        # print(self.tendency)


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
        todate=datetime(2021, 1, 26, 4, 0))  # Конечная дата и время приема исторических данных (Не входит)
    cerebro.adddata(data)  # Привязываем исторические данные
    cerebro.broker.setcash(100000)  # Стартовый капитал для "бумажной" торговли
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)  # Кол-во в штуках для покупки/продажи
    cerebro.run()  # Запуск торговой системы
    cerebro.plot(style='bar', bardown='grey')  # Рисуем график. Требуется matplotlib версии 3.2.2
    # (pip install matplotlib==3.2.2)
