from models import ItemMeta
from typing import Iterable


class CsvModel:
    """
    CSVのデータを商品ごとにまとめるためのクラス
    """
    def __init__(self):
        self.__item_id = ''
        self.__item_buyma = []
        self.__item_shop = []

    def __str__(self):
        return_str = '商品ID:' + self.__item_id + '   '
        return_str += 'Buyma:' + str(self.__item_buyma) + '   '
        return_str += '仕入れ先:' + str(self.__item_shop) + '   '
        return

    # 商品ID
    @property
    def item_id(self):
        return self.__item_id

    @item_id.setter
    def item_id(self, item_id):
        self.__item_id = item_id

    # 商品メタ(buyma)
    @property
    def item_buyma(self) -> Iterable[ItemMeta]:
        return self.__item_buyma

    @item_buyma.setter
    def item_buyma(self, buyma_item_meta: ItemMeta):
        self.__item_buyma.append(buyma_item_meta)

    # 商品メタ(仕入れ先)
    @property
    def item_shop(self) -> Iterable[ItemMeta]:
        return self.__item_shop

    @item_shop.setter
    def item_shop(self, item_meta: ItemMeta):
        self.__item_shop.append(item_meta)
