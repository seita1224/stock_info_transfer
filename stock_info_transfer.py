from typing import List

from itemscraping import Buyma, Asos
from csvparse import CsvParse
import logout


logout.output_log_info(None, ('-' * 20) + '在庫情報更新処理開始' + ('-' * 20))

csv_parse = CsvParse('./input_data/input_csv.csv')

buyma_item_list = csv_parse.create_buyma_item()

asos = Asos()
buyma_item_update_list = []

for buyma_item in buyma_item_list:
    buyma_item_update_list.append(asos.update_item_stock(buyma_item))

by = Buyma()

by.input_data(buyma_item_list=buyma_item_list)

logout.output_log_info(None, ('-' * 20) + '在庫情報更新処理終了' + ('-' * 20))
