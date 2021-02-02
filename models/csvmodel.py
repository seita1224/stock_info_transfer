from models import ItemMeta
from typing import Iterable, List


class CsvModel:
    """
    CSVのデータを商品ごとにまとめるためのクラス
    """
    def __init__(self):
        self.__item_id = ''
        self.__item_info = []

    def __str__(self):
        return_str = '商品ID:' + self.__item_id + '   '
        return_str += 'Buyma:' + str(self.__item_info) + '   '
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
    def item_info(self) -> List[ItemMeta]:
        return self.__item_info

    @item_info.setter
    def item_info(self, item_info: ItemMeta):
        if isinstance(item_info, ItemMeta):
            self.__item_info.append(item_info)
        elif isinstance(item_info, list):
            if all(isinstance(meta, ItemMeta) for meta in item_info):
                self.__item_info = item_info

