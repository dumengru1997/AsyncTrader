
STRATEGY_CREATE = """
```
{describe}
```
Write a quantitative trading strategy class using vnpy according to the above description, with the following requirements:
1. The class inherits `CtaTemplate` and is named `AutoStrategy`.

2. The following methods can be implemented depending on the strategy type: 
- on_init: Callback when strategy is inited.
- on_start: Callback when strategy is started.
- on_stop: Callback when strategy is stopped.
- on_bar: Callback of new bar data update.
- on_trade: Callback of new trade data update.
- on_order: Callback of new order data update.

3. You can use the following tool packages
- import numpy as np
- from pandas import DataFrame
- import talib.abstract as ta

Output format is as follows:
auto_strategy.py
```python
[strategy code]
```
```

Output format is as follows:
auto_strategy.py
```python
[strategy code]
```
"""

