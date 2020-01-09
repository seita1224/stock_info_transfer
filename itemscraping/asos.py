"""
Asosのサイトの操作を行う用のクラス
このクラスを使用しAsosについては操作を行う
Todo:
    このクラスは抽象化対象
    ソースを書き込む
"""

from bs4 import BeautifulSoup
from itemscraping.siteaccess import SiteAccess


class Asos():
    """
    asosのサイトの操作を行う用のクラス
    """
    # スクレイピング用
    bf = None

    # 商品名
    item_name = None

    def __init__(self):
        """
        Todo:
            初期化に何が必要かは後ほど検討
        """
        pass

    def item_stock_info(self):
        """
        在庫の取得のデータの有無の取得
        Returns:
            list<str>: 商品の在庫一覧
        """
        sa = SiteAccess()
        self.bf = BeautifulSoup(sa.script_compile(url), 'html.parser')
        self.item_name = item_name

        item_info = self.bf.find(id='main-size-select-0').find_all('option')

        # 商品のサイズリスト
        item_info_list = []

        for item in item_info:
            item_info_list.append(item.string)

        return item_info_list



