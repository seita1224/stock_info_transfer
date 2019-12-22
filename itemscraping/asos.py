from bs4 import BeautifulSoup
from itemscraping.scriptcomp import ScriptCompyle

class Asos():
    """
    asosの商品スクレイピング用オブジェクト
    このオブジェクトを使用して在庫の有無を取得する
    """
    # スクレイピング用
    bf = None

    # 商品名
    item_name = None

    def __init__(self,url,item_name):
        """
        Args:
            @param url(str):在庫取得先のURL
            @param item_name(str):商品名
        """
        sc = ScriptCompyle(url)
        self.bf = BeautifulSoup(sc.script_compaill(),'html.parser')
        self.item_name = item_name


    def item_stock_info(self):
        """
        在庫の取得のデータの有無の取得
        Return:
            @return item_info_list(list<str>):商品の在庫有無
        """
        item_info = self.bf.find(id='main-size-select-0').find_all('option')

        # 商品のサイズリスト
        item_info_list = []

        for item in item_info:
            item_info_list.append(item.string)

        return item_info_list



