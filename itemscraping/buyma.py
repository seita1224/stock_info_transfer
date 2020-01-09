"""
Buymaのサイトの操作を行う用のクラス
このクラスを使用しBuymaについては操作を行う
Todo:
    このクラスは抽象化対象
    ソースを書き込む
"""

from bs4 import BeautifulSoup
from itemscraping.siteaccess import SiteAccess


class Buyma():

    def __init__(self):
        """
        インスタンス化を行った時点でログインを行う
        """
        pass

    def get_sells_item_list(self):
        """
        出品している商品の情報を抽出し、一覧を返す
        Returns:
            list: 出品している商品のリスト
        """
        pass
