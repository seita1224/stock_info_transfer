from itemscraping import Buyma, Asos
from csvparse import CsvParse
import logout

# 在庫情報取得用のオブジェクト初期化
by = Buyma()
csv_parse = CsvParse('./input_data/input_csv.csv')

# Buyma、csvから商品IDの取得
buyma_item_id_list = by.get_item_id_list()
csv_item_id_list = csv_parse.get_item_id_list()

# 在庫情報更新対象商品がbuyma上の商品と一致しているかの検証
item_id_stock_check = list(set(buyma_item_id_list) & set(csv_item_id_list))        # 在庫確認対象商品ID

# 入力された商品の色情報→サイズの順番で情報が一致しているかの検証
item_color_stock_check = dict()
item_size_stock_check = dict()

for item_id in item_id_stock_check:
    # 同じ商品IDのサイズの取り出し
    buyma_colors = by.get_item_color_list(item_id=item_id)
    csv_colors = csv_parse.get_item_color_list_for_buyma(item_id=item_id)
    item_color_stock_check[item_id] = list(set(buyma_colors) & set(csv_colors))

    # 同じ商品IDのサイズの取り出し
    buyma_sizes = by.get_item_size_list(item_id=item_id)
    csv_sizes = csv_parse.get_item_size_list_for_buyma(item_id=item_id)
    item_size_stock_check[item_id] = list(set(buyma_sizes) & set(csv_sizes))

# 色、サイズ共にBuyma,csvに存在する商品IDの割り出し
item_id_existence_color = list(item_color_stock_check.keys())
item_id_existence_size = list(item_size_stock_check.keys())
item_id_buyma_csv_exists = list(set(item_id_existence_color) & set(item_id_existence_size))

logout.output_log_info(class_obj=None, log_message='CSV、BUYMAの商品情報が一致した商品ID:' + str(item_id_buyma_csv_exists))

# 仕入れ先URLの取得
item_url_stock = dict()
for item_id in item_id_buyma_csv_exists:
    for item_color in item_color_stock_check[item_id]:
        for item_size in item_size_stock_check[item_id]:
            item_url_stock[item_id] = csv_parse.get_item_url_list_for_shop(item_id=item_id,
                                                                           color=str(item_color),
                                                                           size=str(item_size))

# ASOS(仕入れ先)から商品の存在しているサイズの取得
asos = Asos()
asos_item_size = dict()
item_id_transfer_target = []

for item_id_for_shop in item_url_stock:
    for item_url in item_url_stock[item_id_for_shop]:
        try:
            asos_item_size[item_id_for_shop] = asos.item_stock_info(item_url)
            # CSV、buyma、仕入れ先の全てが一致した商品IDを在庫確認対象とする
            item_id_transfer_target.append(item_id_for_shop)

        except Exception as e:
            # TODO: 例外処理が起こった時他の対応でエラーを知らせる
            logout.output_log_error(class_obj=None, log_message='仕入れ先商品情報取得エラー商品ID:' + str(item_id_for_shop))
            raise e

logout.output_log_info(class_obj=None, log_message='更新対象商品ID:' + str(item_id_transfer_target))

"""
    TODO: item_id_transfer_targetの商品IDを対象に商品の在庫の情報を更新をする
          基本的ににはBuyma.pyから出てきたデータと、asos_item_sizeの内容を比較する
          Asosから出てくるサイズ存在するものと存在しないものに分けるべきか？　→
"""













