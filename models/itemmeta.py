from __future__ import annotations
from models.existence import Existence


class ItemMeta:
    def __init__(self, color='', size='', shop_size='', existence=Existence.NO_INPUT, url=''):
        self.__color = color
        self.__size = size
        self.__shop_size = shop_size
        self.__existence = existence
        self.__url = url

    def __str__(self):
        return '色:' + self.__color + ','\
               ' サイズ(販売先):' + self.__size + ','\
               ' サイズ(仕入れ先):' + self.__shop_size + ','\
               ' 商品在庫状況:' + str(self.__existence) + '\n'

    def __eq__(self, item_meta: __class__) -> bool:
        if self.size == item_meta.size and self.color == item_meta.color:
            return True
        else:
            return False

    @property
    def color(self) -> str:
        return self.__color

    @color.setter
    def color(self, color):
        self.__color = color

    @property
    def size(self) -> str:
        return self.__size

    @size.setter
    def size(self, size):
        self.__size = size

    @property
    def existence(self) -> Existence:
        return self.__existence

    @existence.setter
    def existence(self, existence: Existence):
        self.__existence = existence

    @property
    def shop_size(self) -> str:
        return self.__shop_size

    @shop_size.setter
    def shop_size(self, shop_size):
        self.__shop_size = shop_size

    @property
    def url(self) -> str:
        return str(self.__url)

    @url.setter
    def url(self, url):
        self.__url = url
