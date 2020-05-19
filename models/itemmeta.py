class ItemMeta:

    def __init__(self, color='', size='', existence=False, url=''):
        self.__color = color
        self.__size = size
        self.__existence = existence
        self.__url = url

    def __str__(self):
        return '色:' + self.__color + ' サイズ:' + self.__size + '  商品在庫状況:' + str(self.__existence)

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
    def existence(self) -> bool:
        return self.__existence

    @existence.setter
    def existence(self, existence):
        self.__existence = existence

    @property
    def url(self) -> str:
        return str(self.__url)

    @url.setter
    def url(self, url):
        self.__url = url
