from typing import List

from itemscraping import Buyma, Asos
from csvparse import CsvParse
import logout

# 在庫情報取得用のオブジェクト初期化
from models import BuymaItem, ItemMeta

by = Buyma()
csv_parse = CsvParse('./input_data/input_csv.csv')

# -----------------    BuymaとCSVの商品情報が一致している物の検索   -----------------
# Buyma、csvから商品IDの取得
buyma_item_id_list = by.get_item_id_list()
csv_item_id_list = csv_parse.get_item_id_list()

# 在庫情報更新対象商品がbuyma上の商品と一致しているかの検証
logout.output_log_debug(None, 'Buyma上の商品ID: ' + str(buyma_item_id_list))
logout.output_log_debug(None, 'csv上の商品ID: ' + str(csv_item_id_list))
item_id_stock_check = list(set(buyma_item_id_list) & set(csv_item_id_list))        # 在庫確認対象商品ID
logout.output_log_debug(None, 'Buyma、CSVどちらにも存在したもの: ' + str(item_id_stock_check))

# 入力された商品の色情報→サイズの順番で情報が一致しているかの検証
item_color_stock_check = dict()
item_size_stock_check = dict()
item_buyma_csv_exists = dict()

for item_id in item_id_stock_check:
    item_buyma_csv_exists[item_id]: List[ItemMeta]

    # 同じ商品IDの色の取り出し
    buyma_colors = by.get_item_color_list(item_id=item_id)
    csv_colors = csv_parse.get_item_color_list_for_buyma(item_id=item_id)
    item_color_stock_check[item_id] = list(set(buyma_colors) & set(csv_colors))

    # 同じ商品IDのサイズの取り出し
    for color in item_color_stock_check[item_id]:
        buyma_sizes = by.get_item_size_list(item_id=item_id, item_color=color)
        csv_sizes = csv_parse.get_item_size_list_for_buyma(item_id=item_id, item_color=color)
        item_size_stock_check = list(set(buyma_sizes) & set(csv_sizes))
        if item_id in item_buyma_csv_exists:
            item_buyma_csv_exists[item_id].extend([ItemMeta(color=color, size=size) for size in item_size_stock_check])
        else:
            item_buyma_csv_exists[item_id] = [ItemMeta(color=color, size=size) for size in item_size_stock_check]

# -----------------    仕入れ先(ASOS)の在庫情報の取得   -----------------
# ASOSから商品情報を取得するためのオブジェクト
asos = Asos()
asos_item_exists_size = dict()
asos_item_not_exists_size = dict()
target_input_itme_id = set()

# CSVから商品URLへアクセスを行い商品が存在しているサイズを取得
for item_id in item_buyma_csv_exists.keys():
    for item_meta in item_buyma_csv_exists[item_id]:
        url = csv_parse.get_item_url_list_for_shop(item_id=item_id,
                                                   color=item_meta.color,
                                                   size=item_meta.size)

        # URLが空の場合はCSVデータの中に色とサイズの組み合わせがない場合
        if url is None: continue
        try:
            # ASOS内のサイズとの比較用にサイズの抽出
            item_size = [meta.size for meta in item_buyma_csv_exists[item_id]]

            # ASOS内に存在している商品サイズを取得
            asos_item_exists_size = list(set(asos.get_item_stock(url)) & set(item_size))

            # 商品の在庫がない商品(ASOSから商品サイズが取得できなかったものかつCSVに商品が存在しているもの)
            asos_item_not_exists_size = list(set(asos.get_item_nothing_stock(url)) & set(item_size))

            # 在庫が存在するものに関しての在庫情報を更新する
            for asos_item_size in asos_item_exists_size:
                if item_meta.size == asos_item_size:
                    item_meta.existence = True

            # 在庫が存在しないものに関しての在庫情報を更新する
            for asos_item_size in asos_item_not_exists_size:
                if item_meta.size == asos_item_size:
                    item_meta.existence = False

        except Exception as err:
            logout.output_log_error(class_obj=None, log_message='仕入れ先商品情報取得エラー商品ID:' + str(item_id), err=err)
            raise err

# 入力用商品情報の作成
for item_id in item_buyma_csv_exists.keys():
    buyma_item = BuymaItem(item_id=item_id, item_name='', item_info=list(item_buyma_csv_exists[item_id]))

    # 在庫情報の入力
    logout.output_log_info(class_obj=None, log_message='入力対象商品: ' + str(buyma_item))
    by.input_item_stock(buyma_item)

# 商品在庫が全てない商品をCSV化する
by.output_csv_nothing_stock()

by.close()
asos.close()
