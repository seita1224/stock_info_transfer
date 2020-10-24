"""
Asosのサイトの操作を行う用のクラス
このクラスを使用しAsosについては操作を行う
Todo:
    このクラスは抽象化対象
    ソースを書き込む
"""

from bs4 import BeautifulSoup
from itemscraping.siteaccess import SiteAccess
from itemscraping.sitesmeta import SitesMeta



class Asos():
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
        self.meta = SitesMeta().get_site_meta('BuySite.Asos')
        self.site_access = SiteAccess()

    def __del__(self):
        del self.site_access

    def get_item_stock(self, item_url) -> list:
        """
        在庫の取得のデータの有無の取得
        Returns:
            list<str>: 商品の在庫一覧
        """
        # URLからHTMLの取得
        bf = BeautifulSoup(self.site_access.script_compile(input_url=item_url), 'html.parser')

        # サイト上のサイズの内容を選択するためのCSSセレクター
        item_stock_meta = self.meta['ItemOfInfo']['ItemSizeList']['ItemSizeListCssSelector']

        # サイズの情報を取得する
        item_stock_info = bf.select(item_stock_meta[0])[0].find_all(item_stock_meta[1])

        # 商品のサイズリスト
        item_info_list = []

        for item in item_stock_info:
            if ' - Not available' not in item.text:
                item_info_list.append(item.text)

        return item_info_list

    def get_item_not_found_stock(self, item_url) -> list:
        """
        在庫の取得のデータの有無の取得
        Returns:
            list<str>: 商品の在庫一覧
        """
        # URLからHTMLの取得
        bf = BeautifulSoup(self.site_access.script_compile(input_url=item_url), 'html.parser')

        # サイト上のサイズの内容を選択するためのCSSセレクター
        item_stock_meta = self.meta['ItemOfInfo']['ItemSizeList']['ItemSizeListCssSelector']

        # サイズの情報を取得する
        item_stock_info = bf.select(item_stock_meta[0])[0].find_all(item_stock_meta[1])

        # 商品のサイズリスト
        item_info_list = []

        for item in item_stock_info:
            if ' - Not available' in item.text:
                item_info_list.append(item.text)

        return item_info_list


