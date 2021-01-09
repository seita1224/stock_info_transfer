"""
Asosのサイトの操作を行う用のクラス
このクラスを使用しAsosについては操作を行う
"""

from bs4 import BeautifulSoup

import logout
from itemscraping.siteaccess import SiteAccess


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

        # 在庫が全て無い場合
        if self.is_out_stock(bf):
            logout.output_log_debug(self, '商品サイズ取得できませんでした。')
            return list()

        # サイズの情報を取得する
        item_stock_info = bf.select('#main-size-select-0 > option')
        logout.output_log_debug(self, '抽出サイズリスト:' + str(item_stock_info))

        # 商品のサイズリスト
        item_info_list = []

        for item in [size for i, size in enumerate(item_stock_info) if i != 0]:
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

        # 在庫が全て無い場合
        if self.is_out_stock(bf):
            logout.output_log_debug(self, '商品サイズ取得できませんでした。')
            return list()

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

    def is_out_stock(self, bf: BeautifulSoup) -> bool:
        """
        このメソッドはASOSのサイト上に商品全てが売り切れた際に出力されるメッセージを検出する

        Param:
            item_url(str): 検出対象のURL

        Returns:
            bool: 商品が存在する場合        : True
                　商品全てが売り切れだった場合: False

        """
        item_info = bf.select('#main-size-select-0 > option')
        if item_info is None:
            logout.output_log_debug(self, '商品全てが売り切れ')
            return False

        return True

    def close(self):
        """
        ブラウザの終了
        """
        self.site_access.exit()
