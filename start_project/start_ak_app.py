from trading_system.akshare_system.start_akshare import start_auto


if __name__ == '__main__':
    # 1. 输入需要查询的数据
    result = start_auto("获取交易日历")
    print(result)
    # result.to_csv("temp.csv", encoding="gbk")
