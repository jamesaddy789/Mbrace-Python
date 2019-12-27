import re

name = 'Composite_24_6F_28_A0_DA_30_2019-12-16_to_24_6F_28_A0_DA_30_2020-01-25.bin'
date_match_list = re.findall(r"\d{4}-\d{2}-\d{2}", name)
for date in date_match_list:
    print(date)

