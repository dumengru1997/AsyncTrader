from trading_system.freqtrade_system.start_freqtrade import start_stepwise, start_stepwise
from trading_system.trading_tools import web_strategy_tool


if __name__ == '__main__':
    # start_auto("trader_freqtrade.txt", "ft_workspace", add_tools=[web_strategy_tool])

    start_stepwise("trader_freqtrade.txt", "ft_workspace", add_tools=[web_strategy_tool])
