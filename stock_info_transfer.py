from typing import List

from itemscraping import Buyma, Asos
from csvparse import CsvParse
import logout

# 在庫情報取得用のオブジェクト初期化
from models import BuymaItem, ItemMeta
from models.existence import Existence

logout.output_log_info(None, '-------------------------------------------------------在庫情報更新処理開始-------------------------------------------------------')

by = Buyma()
csv_parse = CsvParse('./input_data/input_csv.csv')

# -----------------    BuymaとCSVの商品情報が一致している物の検索   -----------------
# Buyma、csvから商品IDの取得
buyma_item_id_list = by.get_item_id_list()
csv_item_id_list = csv_parse.get_item_id_list()

# 在庫情報更新対象商品がbuyma上の商品と一致しているかの検証
logout.output_log_debug(None, 'Buyma上の商品ID: ' + str(buyma_item_id_list))
logout.output_log_debug(None, 'csv上の商品ID: ' + str(csv_item_id_list))
item_id_stock_check = list(set(buyma_item_id_list) & set(csv_item_id_list))  # 在庫確認対象商品ID
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
        # item_buyma_csv_existsに存在するなら商品情報のリストに結合する
        if item_id in item_buyma_csv_exists:
            item_buyma_csv_exists[item_id].extend([ItemMeta(color=color,
                                                            size=size,
                                                            shop_size=csv_parse.get_item_size_for_shop(item_id=item_id,
                                                                                                       item_color=color,
                                                                                                       item_buyma_size=size),
                                                            existence=by.get_item_existence(item_id, color, size))
                                                   for size in item_size_stock_check])
        else:
            item_buyma_csv_exists[item_id] = [ItemMeta(color=color,
                                                       size=size,
                                                       shop_size=csv_parse.get_item_size_for_shop(item_id=item_id,
                                                                                                  item_color=color,
                                                                                                  item_buyma_size=size),
                                                       existence=by.get_item_existence(item_id, color, size))
                                              for size in item_size_stock_check]

# -----------------    仕入れ先(ASOS)の在庫情報の取得   -----------------
# ASOSから商品情報を取得するためのオブジェクト
asos = Asos()
asos_item_exists_size = dict()
target_input_itme_id = set()

# CSVから商品URLへアクセスを行い商品が存在しているサイズを取得
for item_id in item_buyma_csv_exists.keys():
    for i, item_meta in enumerate(item_buyma_csv_exists[item_id]):
        url = csv_parse.get_item_url_list_for_shop(item_id=item_id,
                                                   color=item_meta.color,
                                                   size=item_meta.size)

        # URLが空の場合はCSVデータの中に色とサイズの組み合わせがない場合
        if url is None: continue
        try:
            # ASOS内のサイズとの比較用にサイズの抽出
            item_size = [meta.size for meta in item_buyma_csv_exists[item_id]]

            # ASOS内に存在している商品サイズを取得
            asos_item_exists_size = asos.get_item_stock(url)

            # 在庫が存在するものに関しての在庫情報を更新する
            for asos_item_size in asos_item_exists_size.keys():
                if item_meta.shop_size == asos_item_size:
                    # 「手元に在庫あり」の商品は在庫情報を変更しない(商品情報更新前に対象から外す)
                    if not item_buyma_csv_exists[item_id][i].existence == Existence.IN_STOCK_AT_HAND:
                        item_buyma_csv_exists[item_id][i].existence = asos_item_exists_size[asos_item_size]

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

logout.output_log_info(None, '-------------------------------------------------------在庫情報更新処理終了-------------------------------------------------------')
