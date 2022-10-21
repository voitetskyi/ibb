import backtrader as bt
from datetime import datetime

import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Grid, Line, LinearAxis, Plot


pd.set_option('display.max_rows', None)


class ShowPlot:

    def __init__(self):
        df = pd.read_csv('../data/quotes_es.globex_1mm.csv', parse_dates=True)
        start_date = 20210126110000
        end_date = 20210126125900
        self.df = df[df.time.between(start_date, end_date)]
        inc = self.df.close > self.df.open
        dec = self.df.open > self.df.close
        w = 0.5
        tools = "pan,wheel_zoom,box_zoom,reset,save"
        self.p = figure(x_axis_type="datetime", tools=tools, width=1500)
        self.p.grid.grid_line_alpha = 0.3
        # self.p.xaxis.major_label_overrides = {
        #     i: date.strftime('%b %d') for i, date in enumerate(pd.to_datetime(df['time']))
        # }
        # self.p.xaxis.bounds = (0, df.index[-1])
        # self.p.x_range.range_padding = 0.05
        self.p.segment(self.df.index, self.df.high, self.df.index, self.df.low, color="black")
        self.p.vbar(self.df.index[inc], w, self.df.open[inc], self.df.close[inc], fill_color="#D5E1DD",
                    line_color="black")
        self.p.vbar(self.df.index[dec], w, self.df.open[dec], self.df.close[dec], fill_color="black",
                    line_color="black")

    def add_tendency(self, tendency):
        index = []
        for i in range(0, 120):
            index.append(i)
        df = pd.DataFrame(index=index, columns=['y'])
        for i in tendency:
            df.loc[i['i'], 'y'] = i['price']
        # self.p.line(x=df.index, y=df.y, line_color='red')
        print(df)

    def show(self):
        show(self.p)


class TwoEfforts(bt.ind.PeriodN):
    lines = ('zigzag',)
    plotinfo = dict(
        subplot=False,
        plotlinelabels=True,
        plotlinevalues=True,
        plotvaluetags=True,
    )
    # plotlines = dict(zigzag=dict(_name='zigzag', color='red', ls='--', _skipnan=True),)
    params = (('period', 2),)

    def __init__(self):
        super(TwoEfforts, self).__init__()
        self.tendency = []
        self.zones = []
        self.status = 0
        self.counter = 0
        self.plot = ShowPlot()

    # def show_plot(self):
    #     show(self.p)

    def short_or_long(self):
        if self.tendency[-4]['type'] == 'LL':
            if self.tendency[-4]['price'] < self.tendency[-2]['price']\
                    and self.tendency[-3]['price'] < self.tendency[-1]['price']:
                self.status = 'SHORT'
            if self.tendency[-4]['type'] == 'HH':
                if self.tendency[-4]['price'] > self.tendency[-2]['price']\
                        and self.tendency[-3]['price'] > self.tendency[-1]['price']:
                    self.status = 'LONG'

    def add_zone(self, start_time, start_price, end_time, end_price, zone_type):
        self.zones.append({'start_time': start_time, 'start_price': start_price, 'end_time': end_time,
                           'end_price': end_price, 'zone_type': zone_type})

    def two_efforts(self):
        if self.tendency[-1]['type'] == 'LL':
            if self.data.close[0] > self.tendency[-2]['price']:
                zone_type = 'two_imp' if self.status == 'SHORT' else 'tendency_win'
                self.add_zone(self.tendency[-3]['time'], self.tendency[-1]['price'], self.get_time(0),
                              self.tendency[-2]['price'], zone_type)
        if self.tendency[-1]['type'] == 'HH':
            if self.data.close[0] < self.tendency[-2]['price']:
                zone_type = 'two_imp' if self.status == 'LONG' else 'tendency_win'
                self.add_zone(self.tendency[-3]['time'], self.tendency[-1]['price'], self.get_time(0),
                              self.tendency[-2]['price'], zone_type)

    def get_time(self, index):
        return self.data.num2date(self.data.datetime[index])

    def append_tendency_point(self, index, type_of_point):
        price = self.data.high[index] if type_of_point == 'HH' else self.data.low[index]
        self.tendency.append({'time': self.get_time(index), 'price': price, 'type': type_of_point, 'i': self.counter})

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

    def tendency_function(self):
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

    def next(self):
        self.tendency_function()
        if self.status == 0 and len(self.tendency) > 4:
            self.short_or_long()
        if self.status != 0:
            self.two_efforts()
        self.counter += 1
        if self.counter == 119:
            print(self.counter)
            self.plot.add_tendency(self.tendency)
            self.plot.show()
            print(self.tendency)
        # print(self.zones)


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    cerebro = bt.Cerebro(stdstats=False)  # Инициируем "движок" BT, убираем стандартную статистику
    # cerebro.addobserver(bt.observers.Value)  # Отображаем кривую доходности
    cerebro.addobserver(bt.observers.BuySell, barplot=True, bardist=0.0001)  # Для небольшого временнОго интервала
    # нужно уменьшить дистанцию от баров до маркеров входа/выхода
    # cerebro.addstrategy(Simple)  # Добавляем торговую систему
    cerebro.addindicator(TwoEfforts)
    data = bt.feeds.GenericCSVData(
        dataname='../data/quotes_es.globex_1mm.csv',  # Файл для импорта
        separator=',',  # Колонки разделены табуляцией
        dtformat='%Y%m%d%H%M%S',  # Формат даты/времени DD.MM.YYYY HH:MI
        openinterest=-1,  # Открытого интереса в файле нет
        timeframe=bt.TimeFrame.Minutes,  # Для временнОго интервала отличного от дневок нужно его указать
        compression=1,  # Для миннутного интервала, отличного от 1, его нужно указать
        fromdate=datetime(2021, 1, 26, 11, 0),  # Начальная дата и время приема исторических данных (Входит)
        todate=datetime(2021, 1, 26, 12, 59))  # Конечная дата и время приема исторических данных (Не входит)
    cerebro.adddata(data)  # Привязываем исторические данные
    cerebro.broker.setcash(100000)  # Стартовый капитал для "бумажной" торговли
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)  # Кол-во в штуках для покупки/продажи
    cerebro.run()  # Запуск торговой системы
    # cerebro.plot(style='bar', bardown='grey', volume=False)  # Рисуем график. Требуется matplotlib версии 3.2.2
    # (pip install matplotlib==3.2.2)
