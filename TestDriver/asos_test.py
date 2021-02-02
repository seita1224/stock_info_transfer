from copy import deepcopy

import logout
from csvparse import CsvParse
from itemscraping import Asos

asos = Asos()
csv_parse = CsvParse('/Users/seita/Program/python/stock_info_transfer/TestDriver/TestData/testdata.csv')
buyma_item_list = csv_parse.create_buyma_item()

buyma_item_update_list = []
before = deepcopy(buyma_item_list)

print('更新前')
for buyma_item in buyma_item_list:
    print(buyma_item)

for buyma_item in buyma_item_list:
    buyma_item_update_list.append(asos.update_item_stock(buyma_item))

after = buyma_item_update_list

for buyma_item in buyma_item_list:
    print(buyma_item)
print('更新後')

for b, a in zip(before, after):
    b_s = str(b)
    a_s = str(a)
    if a == b:
        print('更新前:', b_s)
        print('更新後:', a_s)
