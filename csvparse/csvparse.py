import logout
from models import CsvModel, BuymaItem, Existence
from models import ItemMeta
from typing import List


class CsvParse:
    """
    商品情報を更新したいcsvが記載されているcsvを以下の形のdict形式に変換する
    取得するcsvの形式: 商品ID(buyma),商品URL(仕入先),サイズ(buyma),サイズ(仕入先),色情報(buyma)
    """

    def __init__(self, file_path: str):
        self.__file_path = file_path
        self.__csv_text_lines = self.get_csv_text()
        self.__csv_item_data: List[CsvModel] = self.create_csv_data()

    def get_csv_text(self):
        """
        Returns:
            str: 解析を行うCSVのテキスト情報
        """
        try:
            with open(self.__file_path, mode='r', encoding='utf-8') as f:
                return f.readlines()

        except IOError as e:
            logout.output_log_error(self, '指定されたパスにCSVファイルが存在しません', err=e)
            raise e

    def create_csv_data(self) -> list:
        """
        CSVテキストの内容をデータを商品IDの種類分リストにして返す
        Returns:
          list: 商品IDごとのCsvModel型オブジェクト
        """
        item_id_list = []  # 商品ID
        item_color_list = []  # 色情報
        item_buyma_size_list = []  # Buymaのサイズ名
        item_shop_size_list = []  # 仕入れ先のサイズ名
        item_shop_url_list = []  # 仕入れ先の商品URL

        # 各CSVカラムをリストに格納
        for i, csv_row in enumerate(self.__csv_text_lines):
            # ヘッダーを省く
            if i != 0:
                item_info = csv_row.split(',')
                item_info = list(map(self.clear_text, item_info))

                item_id_list.append(item_info[0])
                item_color_list.append(item_info[4])
                item_buyma_size_list.append(item_info[2])
                item_shop_size_list.append(item_info[3])
                item_shop_url_list.append(item_info[1])

        # 商品IDの重複を削除しCSV内の商品情報を1つの変数でまとめる
        item_id_set = set(item_id_list)
        item_csv_list = []

        for set_in_item_id in item_id_set:
            item_csv = CsvModel()  # csvの解析結果
            for i, list_in_item_id in enumerate(item_id_list):
                if set_in_item_id == list_in_item_id:
                    item_csv.item_id = list_in_item_id

                    # 色、サイズの情報をそれぞれ格納(buyma)
                    item_meta = ItemMeta(color=item_color_list[i],
                                         size=item_buyma_size_list[i],
                                         shop_size=item_shop_size_list[i],
                                         url=item_shop_url_list[i])
                    item_csv.item_info = item_meta

            # 戻り値用にデータの格納
            item_csv_list.append(item_csv)

        return item_csv_list

    def get_item_id_list(self) -> list:
        """
        商品IDのリストを返す
        Returns:
            list: 商品IDリスト
        """
        # 商品IDのリスト
        item_id_list = []

        for item in self.__csv_item_data:
            item_id_list.append(item.item_id)

        return item_id_list

    def get_item_size_list_for_buyma(self, item_id: str, item_color: str) -> list:
        """
        商品サイズのリストを返す(buyma)
        Args:
            item_id: 商品ID
            item_color: 色
        Returns:
            list: 商品サイズリスト
        """
        # 商品サイズリスト
        item_size_list = []

        # 引数の商品IDのサイズを抽出
        for item in self.__csv_item_data:
            if item.item_id != item_id:
                continue
            item_size_list = [item.item_info[i].size for i in range(len(item.item_info)) if
                              item_color == item.item_info[i].color]

        return item_size_list

    def get_item_color_list_for_buyma(self, item_id: str) -> list:
        """
        商品色のリストを返す(buyma)
        Args:
            item_id: 商品ID
        Returns:
            list: 商品色リスト
        """
        # 商品サイズリスト
        item_color_list = []

        # 引数の商品IDのサイズを抽出
        for item in self.__csv_item_data:
            if item.item_id == item_id:
                item_color_list = [item.item_info[i].color for i in range(len(item.item_info))]

        return item_color_list

    def get_item_size_list_for_shop(self, item_id, item_color: str) -> list:
        """
        商品サイズのリストを返す(仕入れ先)
        Args:
            item_id: 商品ID
            item_color: 色
        Returns:
            list: 商品サイズリスト
        """
        # 商品サイズリスト
        item_size_list = []

        # 引数の商品IDのサイズを抽出
        # 引数の商品IDのサイズを抽出
        for item in self.__csv_item_data:
            if item.item_id != item_id:
                continue
            item_size_list = [item.item_info[i].shop_size for i in range(len(item.item_info)) if
                              item_color == item.item_info[i].color]

        return item_size_list

    def get_item_color_list_for_shop(self, item_id) -> list:
        """
        商品色のリストを返す(仕入れ先)
        今後ショップサイズが増えた時ように残しておく
        Args:
            item_id: 商品ID
        Returns:
            list: 商品色リスト
        """
        # 商品サイズリスト
        item_color_list = []

        # 引数の商品IDのサイズを抽出
        for item in self.__csv_item_data:
            if item.item_id == item_id:
                item_color_list = [item.item_info[i].color for i in range(len(item.item_info))]

        return item_color_list

    def get_item_url_for_shop(self, item_id: str, color: str, size: str) -> str:
        """
        商品URLのリストを返す
        Args:
            item_id: 商品ID
            color: 色
            size: サイズ(仕入れ先)
        Returns:
            str: 商品URL
        """
        # 引数の商品IDのサイズを抽出
        for item in self.__csv_item_data:
            if item.item_id == item_id:
                for item_meta in item.item_info:
                    if item_meta.color == color and item_meta.shop_size == size:
                        return item_meta.url

    def get_item_size_for_shop(self, item_id, item_color, item_buyma_size) -> str:
        """
        ショップ用のsizeの取得
        Args:
            item_id: 商品ID
            item_color: 商品の色
            item_buyma_size: buymaのサイズ
        Returns:
            str: 仕入れ元の商品サイズ
        """
        for item in self.__csv_item_data:
            if item.item_id == item_id:
                for shop_item_list in item.item_info:
                    if shop_item_list.color == item_color and shop_item_list.size == item_buyma_size:
                        return shop_item_list.shop_size
        return ''

    def clear_text(self, target_text: str) -> str:
        return target_text.strip('\n')

    def create_buyma_item(self):
        """
        csvの中身をBuymaItemクラスとして返す
        Returns:
            List[BuymaItem]: csvの中身
        """
        buyma_item_list = []
        item_id_list = self.get_item_id_list()
        for item_index, item_id in enumerate(item_id_list):
            buyma_item_list.append(BuymaItem(item_id=item_id, item_name='', item_info=[]))
            item_color_for_buyma_list = set(self.get_item_color_list_for_buyma(item_id=item_id))
            for item_color in item_color_for_buyma_list:
                item_buyma_size_list = self.get_item_size_list_for_buyma(item_id=item_id, item_color=item_color)
                item_shop_size_list = self.get_item_size_list_for_shop(item_id=item_id, item_color=item_color)
                for item_buyma_size, item_shop_size in zip(item_buyma_size_list, item_shop_size_list):
                    item_meta = ItemMeta(color=item_color,
                                         size=item_buyma_size,
                                         shop_size=item_shop_size,
                                         url=self.get_item_url_for_shop(item_id=item_id, color=item_color, size=item_shop_size),
                                         existence=Existence.NO_INPUT)

                    buyma_item_list[item_index].item_info = item_meta
        return buyma_item_list
