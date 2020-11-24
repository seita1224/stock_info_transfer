"""
Asosのサイトの操作を行う用のクラス
このクラスを使用しAsosについては操作を行う
Todo:
    このクラスは抽象化対象
    ソースを書き込む
"""

from bs4 import BeautifulSoup

import logout
from itemscraping.siteaccess import SiteAccess
from itemscraping.sitesmeta import SitesMeta


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

    def get_item_stock(self, item_url) -> list:
        """
        在庫の取得のデータの有無の取得
        Returns:
            list<str>: 商品の在庫一覧
        """
        logout.output_log_debug(self, '仕入れ先のURL: ' + item_url)

        # URLからHTMLの取得
        bf = BeautifulSoup(self.site_access.script_compile(input_url=item_url, obj=self), 'html.parser')

        # サイズの情報を取得する
        item_stock_info = bf.select('#main-size-select-0 > option')
        logout.output_log_debug(self, '抽出サイズリスト:' + str(item_stock_info))

        # 商品のサイズリスト
        item_info_list = []

        for item in item_stock_info:
            if ' - Not available' not in item.text:
                item_info_list.append(item.text)

        logout.output_log_debug(self, 'ASOSにて検索できたサイズ: ' + str(item_info_list))
        return item_info_list

    def get_item_nothing_stock(self, item_url) -> list:
        """
        在庫の取得のデータの有無の取得
        Returns:
            list<str>: 商品の在庫一覧
        """
        logout.output_log_debug(self, '仕入れ先のURL: ' + item_url)

        # URLからHTMLの取得
        bf = BeautifulSoup(self.site_access.script_compile(input_url=item_url, obj=self), 'html.parser')

        # サイズの情報を取得する
        item_stock_info = bf.select('#main-size-select-0 > option')
        logout.output_log_debug(self, '抽出サイズリスト:' + str(item_stock_info))

        # 商品のサイズリスト
        item_info_list = []

        for item in item_stock_info:
            if ' - Not available' in item.text:
                item_info_list.append(item.text)

        logout.output_log_debug(self, 'ASOSにて検索できたサイズ: ' + str(item_info_list))
        return item_info_list
    # todo: 商品が売り切れだった場合の処理を追加する
    # def outstock_checker(self, bf: BeautifulSoup):
    #     """
    #     このメソッドはASOSのサイト上に商品全てが売り切れた際に出力されるメッセージを検出する
    #
    #     Returns:
    #         bool: 商品全てが売り切れだった場合: True
    #               それ以外                : False
    #     """
    #     outstock = bf.select_one('#oos-label > h3')
    #     if outstock.get_text =

