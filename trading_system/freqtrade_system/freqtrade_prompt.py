
STRATEGY_CREATE = """
```
{describe}
```
Write a quantitative trading strategy class using Freqtrade according to the above description, with the following requirements:
1. The class inherits `IStrategy` and is named `AutoStrategy`.
2. You need to add the following properties and add optimizable parameter spaces:
- can_short={can_short}
- minimal_roi
- stoploss
- trailing_stop

3. Implement the following methods:
- populate_indicators: Populate indicators that will be used in the Buy, Sell, Short, Exit_short strategy
- populate_buy_trend: Based on TA indicators, populates the entry signal for the given dataframe
- populate_sell_trend: Based on TA indicators, populates the exit signal for the given dataframe

4. You can use the following tool packages
- import numpy as np
- from pandas import DataFrame
- import talib.abstract as ta
- from technical.util import resample_to_interval, resampled_merge
- from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter, IStrategy, IntParameter)

5. Instead of using `Parameter` as the parameter value, use `Parameter.value`
eg:
```
buy_fast_period = IntParameter(5, 20, default=10, space='buy')
dataframe['buy_fast_ma'] = ta.SMA(dataframe['close'], timeperiod=self.buy_fast_period.value
```

Output format is as follows:
auto_strategy.py
```python
[strategy code]
```
"""

