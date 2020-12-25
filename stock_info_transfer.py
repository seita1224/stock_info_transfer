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
logout.output_log_debug(None, '入力された商品IDが入力されたもの: ' + str(item_id_stock_check))

# 入力された商品の色情報→サイズの順番で情報が一致しているかの検証
item_color_stock_check = dict()
item_size_stock_check = dict()

for item_id in item_id_stock_check:
    # 同じ商品IDの色の取り出し
    buyma_colors = by.get_item_color_list(item_id=item_id)
    csv_colors = csv_parse.get_item_color_list_for_buyma(item_id=item_id)
    item_color_stock_check[item_id] = list(set(buyma_colors) & set(csv_colors))

    # 同じ商品IDのサイズの取り出し
    buyma_sizes = by.get_item_size_list(item_id=item_id)
    csv_sizes = csv_parse.get_item_size_list_for_buyma(item_id=item_id)
    item_size_stock_check[item_id] = list(set(buyma_sizes) & set(csv_sizes))

    logout.output_log_debug(None, '商品ID: ' + item_id)
    logout.output_log_debug(None, '商品色: ' + str(item_color_stock_check[item_id]))
    logout.output_log_debug(None, '商品サイズ: ' + str(item_size_stock_check[item_id]))

# 色、サイズ共にBuyma,csvに存在する商品IDの割り出し
item_id_existence_color = list(item_color_stock_check.keys())
item_id_existence_size = list(item_size_stock_check.keys())
item_id_buyma_csv_exists = list(set(item_id_existence_color) & set(item_id_existence_size))

logout.output_log_info(None, 'CSV、BUYMAの商品情報が一致した商品ID:' + str(item_id_buyma_csv_exists))

# -----------------    仕入れ先(ASOS)の在庫情報の取得   -----------------
# ASOSから商品情報を取得するためのオブジェクト
asos = Asos()
asos_item_exists_size = dict()
asos_item_not_exists_size = dict()
target_input_itme_id = set()

# CSVから商品URLへアクセスを行い商品が存在しているサイズを取得
for item_id in item_id_buyma_csv_exists:
    for item_color in item_color_stock_check[item_id]:
        for item_size in item_size_stock_check[item_id]:
            url = csv_parse.get_item_url_list_for_shop(item_id=item_id, color=str(item_color), size=str(item_size))
            # URLが空の場合はCSVデータの中に色とサイズの組み合わせがない場合
            if url is None: continue
            try:
                # ASOS内に存在している商品サイズを取得
                asos_item_exists_size[item_id] = list(set(item_size_stock_check[item_id]) & set(asos.get_item_stock(url)))
                # 商品の在庫がない商品(ASOSから商品サイズが取得できなかったものかつCSVに商品が存在しているもの)
                asos_item_not_exists_size[item_id] = list(set(item_size_stock_check[item_id]) &
                                                          set(item_size_stock_check[item_id]) ^
                                                          set(asos_item_exists_size[item_id]))

                # ASOSから商品サイズが取得できた商品IDを入力対象商品として保管しておく
                target_input_itme_id.add(item_id)

            except Exception as err:
                logout.output_log_error(class_obj=None, log_message='仕入れ先商品情報取得エラー商品ID:' + str(item_id), err=err)
                raise err

# 入力用商品情報の作成
for item_id in target_input_itme_id:
    item_info_exists_list = []
    item_info_not_exists_list = []
    for item_color in item_color_stock_check[item_id]:
        # 商品の情報を作成する
        for item_size in asos_item_exists_size[item_id]:
            # 在庫が存在する商品
            item_info_exists_list.append(ItemMeta(color=item_color, size=item_size, existence=True))
        for item_size in asos_item_not_exists_size[item_id]:
            # 在庫が存在しない商品
            item_info_not_exists_list.append(ItemMeta(color=item_color, size=item_size, existence=False))

        buyma_item = BuymaItem(item_id=item_id, item_name='', item_info=list(item_info_exists_list))
        buyma_item.item_info = item_info_not_exists_list

    # 在庫情報の入力
    by.input_item_stock(buyma_item)
