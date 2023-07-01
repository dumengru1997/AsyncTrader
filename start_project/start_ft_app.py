from trading_system.start_app.start_freqtrade import start_auto, start_stepwise
from trading_system.trading_tools import web_strategy_tool


if __name__ == '__main__':
    # Auto mode
    start_auto("trader_freqtrade.txt", "ft_workspace", add_tools=[web_strategy_tool])
    # Interactive mode
    # start_stepwise("trader_freqtrade.txt", "ft_workspace", add_tools=[web_strategy_tool])
