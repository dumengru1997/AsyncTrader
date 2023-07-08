from typing import Dict
import akshare as ak
import json


# 先假设我们有一个字典包含所有可能的函数
AKSHARE_FUNCTIONS_DICT = {
    "futures_zh_minute_sina": ak.futures_zh_minute_sina,
    "get_futures_daily": ak.get_futures_daily,
    "futures_dce_position_rank": ak.futures_dce_position_rank,
    "futures_spot_price": ak.futures_spot_price,
    "futures_spot_price_previous": ak.futures_spot_price_previous,
    "futures_spot_price_daily": ak.futures_spot_price_daily,
    "futures_czce_warehouse_receipt": ak.futures_czce_warehouse_receipt,
    "futures_shfe_warehouse_receipt": ak.futures_shfe_warehouse_receipt,
    "futures_dce_warehouse_receipt": ak.futures_dce_warehouse_receipt,
    "futures_rule": ak.futures_rule,
    "futures_zh_spot": ak.futures_zh_spot,
    "futures_zh_realtime": ak.futures_zh_realtime,
    "futures_main_sina": ak.futures_main_sina,
    "futures_contract_detail": ak.futures_contract_detail,
    "futures_comm_info": ak.futures_comm_info,
}


def function_call(input_dict: Dict[str, str]):
    # 解析函数名和参数
    func_name = input_dict['name']
    args = json.loads(input_dict['arguments'])

    # 从字典中获取函数并调用它
    func = AKSHARE_FUNCTIONS_DICT[func_name]
    return func(**args)
