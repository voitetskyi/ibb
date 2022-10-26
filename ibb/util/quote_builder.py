from datetime import datetime, timedelta


def read_quote_spec(s):
    spec = {'open': -1, 'high': -1, 'low': -1, 'close': -1}
    for i in range(len(s)):
        if s[i] == ' ' or s[i] == '|':
            return spec
        if s[i] == '.':
            continue
        if s[i].isnumeric():
            if i == 0:
                spec['open'] = int(s[i])
            if i == 1:
                spec['high'] = int(s[i])
            if i == 2:
                spec['low'] = int(s[i])
            if i == 3:
                spec['close'] = int(s[i])

    return spec


def str_to_quote(s, start_date=datetime.now(), delta=timedelta(minutes=1)):
    """
    Генератор котировок по строковому шаблону
    Описание котировки |(open)(high)(low)(close)
    каждый параметр может быть числом 1..9 или точкой (.) == 10 которая также обозначает значение по умолчанию
    строка может содержать несколько переносы (причем каждая строка рассматривается как вертикальное продолжение
    предыдущей. Высота строки == 100. Цена для нижней строки == 0
    """
    result = []

    lines = s.split('\n')

    # максимальная длина строки
    length = 0
    for l in lines:
        if len(l) > length:
            length = len(l)

    # выровнять строки по размеру
    for i, _ in enumerate(lines):
        lines[i] = lines[i].ljust(length)

    # проходим по каждой строке и ищем маркер
    for i in range(length):
        parts = []
        for j in reversed(range(len(lines))):
            index = len(lines) - 1 - j
            if lines[j][i] == '|':
                # все что после текущего индекса - это описание бара
                spec = read_quote_spec(lines[j][i+1:])
                parts.append((index + 1, spec))

        if len(parts) > 0:
            # слить все индивидуальные котировки
            low = parts[0][0] * 100 - 100
            high, open, close = low, low, low
            for p in parts:
                p_low = p[0] * 100 - 100
                if p[1]['high'] != -1:
                    high = p_low + 10 * p[1]['high']
                else:
                    high = p_low + 10 * 10

                if p[1]['close'] != -1:
                    close = p_low + 10 * p[1]['close']
                if p[1]['open'] != -1:
                    open = p_low + 10 * p[1]['open']
                if p[1]['low'] != -1:
                    low = p_low + 10 * p[1]['low']

            high = max(high, open, low)
            low = min(high, open, low)

            result.append({'datetime': start_date, 'open': open, 'high': high, 'low': low, 'close': close})
            start_date = start_date + delta

    return result


if __name__ == '__main__':
    quote = """
                  |
                 |  |
         |      |.5.1  |
       |   |  |        |
    |1.5.8   |
    |           
    """

    quotes = str_to_quote(quote, datetime(2020, 1, 1), timedelta(minutes=5))
    for q in quotes:
        print(q)
