import qlib
print(qlib.__version__)

import qlib
# region in [REG_CN, REG_US]
from qlib.constant import REG_CN
provider_uri = "./qlib_data/cn_data"

qlib.init(provider_uri=provider_uri, region=REG_CN)

from qlib.data import D
result = D.calendar(start_time='2020-01-01', end_time='2023-12-31', freq='day')[:2]
print(result)


r"""
# download 1d
python scripts/get_data.py qlib_data --target_dir C:\Users\amprompt\Desktop\github\asynctrader_demo\start_project\qlib_data\cn_data --region cn

# download 1min
python scripts/get_data.py qlib_data --target_dir C:\Users\amprompt\Desktop\github\asynctrader_demo\start_project\qlib_data\cn_data_1min --region cn --interval 1min

python scripts/get_data.py qlib_data --target_dir ./qlib/qlib_data/us_data --region us
"""



