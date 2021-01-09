from __future__ import annotations
from models import ItemMeta
from typing import Iterable, List


class BuymaItem:

    def __init__(self, item_id: str, item_name: str, item_info: list):
        if item_id is None: item_id = ''
        if item_name is None: item_name = ''
        if item_info is None: item_info = []

        self.__item_id = item_id
        self.__item_name = item_name
        self.__item_info: List[ItemMeta] = item_info

    def __str__(self):
        return '商品ID:' + self.__item_id + ' 商品名: ' + self.__item_name + ' 商品情報: ' + str([str(v) for v in self.__item_info])

    def __eq__(self, buyma_item: __class__) -> bool:
        if self.__item_id == BuymaItem.item_id:
            return True
        else:
            return False

    def update_item_info(self, item_info_list: List[ItemMeta]):
        """
        引数で受け取った商品の在庫情報で更新する
        Args:
            item_info_list(List[ItemMeta]): 更新したい商品情報
        """
        for item_info in item_info_list:
            for i, buyma_item_info in enumerate(self.item_info):
                if item_info == buyma_item_info:
                    self.item_info[i] = item_info

    @property
    def item_id(self) -> str:
        return self.__item_id

    @property
    def item_id_nothing_zero(self) -> str:
        return self.__item_id.lstrip('0')

    @item_id.setter
    def item_id(self, item_id):
        self.__item_id = item_id

    @property
    def item_info(self) -> List[ItemMeta]:
        return self.__item_info

    @item_info.setter
    def item_info(self, item_info):
        if isinstance(item_info, ItemMeta):
            self.__item_info.append(item_info)
        elif isinstance(item_info, list):
            if all(isinstance(meta, ItemMeta) for meta in item_info):
                self.__item_info = item_info

