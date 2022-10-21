import numpy as np
import pandas as pd


df = pd.read_csv('quotes_es.globex_1mm.csv',
                 sep=','
                 )
df.loc[:, 'zigzag'] = np.NaN

if df['open'][0] < df['close'][0]:
    self.tendency.append({'time': self.data.datetime[0], 'price': self.data.low[0], 'type': 'MIN'})
    self.tendency2.append({'time': self.data.datetime[0], 'price': self.data.low[0], 'type': 'MIN'})
elif self.data.open[0] > self.data.close:
    self.tendency.append({'time': self.data.datetime[0], 'price': self.data.high[0], 'type': 'MAX'})
    self.tendency2.append({'time': self.data.datetime[0], 'price': self.data.high[0], 'type': 'MAX'})
else:
    if self.data.high - self.data.close > self.data.close - self.data.low:
        self.tendency.append({'time': self.data.datetime[0], 'price': self.data.high[0], 'type': 'MAX'})
        self.tendency2.append({'time': self.data.datetime[0], 'price': self.data.high[0], 'type': 'MAX'})
    else:
        self.tendency.append({'time': self.data.datetime[0], 'price': self.data.low[0], 'type': 'MIN'})
        self.tendency2.append({'time': self.data.datetime[0], 'price': self.data.low[0], 'type': 'MIN'})
print(df[:5])
print(df['open'][0])