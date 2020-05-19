from models import ItemMeta
from typing import Iterable


class BuymaItem:

    def __init__(self, item_id: str, item_name: str, item_info: list):
        if item_id is None: item_id = ''
        if item_name is None: item_name = ''
        if item_info is None: item_info = []

        self.__item_id = item_id
        self.__item_name = item_name
        self.__item_info: list[ItemMeta] = item_info

    def __str__(self):
        return '' \
               '商品ID:' + self.__item_id + ' ' \
               '商品名:' + self.__item_name + ' ' \
               '' + str(self.__item_info[0])

    @property
    def item_id(self):
        return self.__item_id

    @item_id.setter
    def item_id(self, item_id):
        self.__item_id = item_id

    @property
    def item_info(self) -> Iterable[ItemMeta]:
        return self.__item_info

    @item_info.setter
    def item_info(self, item_info: ItemMeta):
        self.__item_info.append(item_info)
