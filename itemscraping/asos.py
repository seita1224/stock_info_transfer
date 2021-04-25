"""
Asosのサイトの操作を行う用のクラス
このクラスを使用しAsosについては操作を行う
"""
from typing import Tuple

from bs4 import BeautifulSoup

import logout
from itemscraping.siteaccess import SiteAccess
from models import Existence, BuymaItem

from util.exception import HtmlException


class Asos:
    """
    asosのサイトの操作を行う用のクラス
    """
    # サイトアクセス用オブジェクト
    site_access = None

    # サイト固有の情報取得用
    meta = None

    def __init__(self):
        """
        コンストラクタ
        """
        self.site_access = SiteAccess()

    def __del__(self):
        del self.site_access

    def get_item_stock(self, item_url) -> Tuple[dict, bool]:
        """
        在庫の取得のデータの有無の取得
        Returns:
            list<str>: 商品の在庫一覧
        """
        logout.output_log_debug(self, '仕入れ先のURL: ' + item_url)

        # URLからHTMLの取得
        bf = BeautifulSoup(self.site_access.script_compile(input_url=item_url, obj=self), 'html.parser')

        retry = 0
        while retry < 3:
            # 在庫が全て無い場合
            if not self.find_not_dropdown(bf):
                if self.out_of_stock(bf):
                    return dict(), False
                else:
                    logout.output_log_debug(self, '商品サイズ取得できませんでした。リトライ回数:' + str(retry))
                    retry += 1
            else:
                break

        if retry == 3:
            raise HtmlException('商品情報が取得できませんでした')

        # サイズの情報を取得する
        item_stock_info = bf.select('#main-size-select-0 > option')
        logout.output_log_debug(self, '抽出サイズリスト:' + str(item_stock_info))

        # 商品のサイズリスト
        item_info_dict = self.create_item_stock_exist(bf)

        return item_info_dict, True

    def find_not_dropdown(self, bf: BeautifulSoup) -> bool:
        """
        ドロップダウンリストが見つからなかった場合
        Param:
            item_url(str): 検出対象のURL
        Returns:
            bool: 商品が存在する場合        : True
                　商品全てが売り切れだった場合: False
        """
        item_info = bf.select('#main-size-select-0 > option')
        if not item_info:
            return False

        return True

    def close(self):
        """
        ブラウザの終了
        """
        self.site_access.exit()

    def update_item_stock(self, item: BuymaItem):
        """
        asosから引数で受け取ったbuymaItemからデータの取得を行う
        Args:
            item(BuymaItem): 商品情報を取得したいURLの情報が入力されているBuymaItem
        Returns:
            BuymaItem: 商品在庫情報が更新されているBuymaItem
        """
        # asosのサイトの在庫リスト
        asos_item_list = []

        item_meta_list = item.item_info
        # 1商品の色、サイズの1つの組み合わせごとにURLアクセスを行い、在庫情報を入力する
        for meta_index, item_meta_search_asos in enumerate(item_meta_list):
            try:
                asos_item_taple = self.get_item_stock(item_meta_search_asos.url)
            except HtmlException as he:
                logout.output_log_error(he, 'urlのアクセスが失敗しました。')
                raise he

            # 引数でもらってきた商品のサイズとasosのサイズが一致している場合は在庫情報を更新する
            if asos_item_taple[1]:
                for asos_item in asos_item_taple[0].keys():
                    if item_meta_search_asos.shop_size == asos_item:
                        item_meta_list[meta_index].existence = asos_item_list[asos_item]
                        break
            else:
                item_meta_list[meta_index].existence = Existence.OUT_OF_STOCK

        item.item_info = item_meta_list

        return item

    def create_item_stock_exist(self, bf: BeautifulSoup) -> dict:
        # サイズの情報を取得する
        item_stock_info = bf.select('#main-size-select-0 > option')
        logout.output_log_debug(self, '抽出サイズリスト:' + str(item_stock_info))

        # 商品のサイズリスト
        item_info_dict = dict()

        for item in [size for i, size in enumerate(item_stock_info) if i != 0]:
            if ' - Not available' not in item.text:
                item_info_dict[str(item.text)] = Existence.IN_STOCK
            else:
                item_info_dict[str(item.text).strip(' - Not available')] = Existence.OUT_OF_STOCK

        logout.output_log_debug(self, 'ASOSにて検索できたサイズ: ' + str(item_info_dict))
        return item_info_dict

    def out_of_stock(self, bf):
        out_of_stock = bf.select('#oos-label > h3')
        if out_of_stock:
            return True

        return False
