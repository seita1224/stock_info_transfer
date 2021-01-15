"""
Buymaのサイトの操作を行う用のクラス
このクラスを使用しBuymaについては操作を行う
Todo:
    このクラスは抽象化対象
"""
import pandas as pd
import traceback

from bs4 import BeautifulSoup
from typing import List

from itemscraping.siteaccess import SiteAccess
from itemscraping.sitesmeta import SitesMeta
from models import ItemMeta, BuymaItem
from models.existence import Existence
import logout
import re

from util.exception import ItemIdException


class Buyma:
    # サイトアクセス用オブジェクト
    site_access = None

    # サイト固有の情報取得用
    meta = None

    def __init__(self):
        """
        インスタンス化を行った時点でログインを行う
        """
        self.meta = SitesMeta().get_site_meta('SellSite.Buyma')
        self.site_access = SiteAccess()
        self.site_access.login(site_meta='SellSite.Buyma')
        self.__buyma_item_list: List[BuymaItem] = []
        self.create_buyam_item_list()

    def create_buyam_item_list(self):
        self.site_access.script_compile('https://www.buyma.com/my/sell/#/')
        self.site_access.change_display_matter()

        while True:
            self.site_access.change_display_matter()
            html = self.site_access.get_now_html()
            item_dict = self.get_sells_item_list(html=html)
            self.__buyma_item_list.extend(self.get_sell_item_stock(item_dict=item_dict))
            if self.site_access.check_next_button():
                self.site_access.click_next_button()
            else:
                break

    def get_sells_item_list(self, html) -> dict:
        """
        出品している商品の情報を抽出し、一覧を返す
        Returns:
            dict(str:str): 出品している商品のリスト<商品ID:商品名>
        """
        try:
            item_list_meta = self.meta['ItemOfInfo']['ItemListInfo']

            # 出品リストのページのHTMLの取得
            bf = BeautifulSoup(self.site_access.script_compile(input_url=item_list_meta['ItemListURL']),
                               'html.parser')
            logout.output_log_debug(self, '出品サイトURL:' + item_list_meta['ItemListURL'])

            # 商品名と商品IDを取得し、辞書型に変換する
            # 商品ID
            item_id_list = bf.find_all(
                attrs={item_list_meta['ItemId']['ClassKey']: re.compile(item_list_meta['ItemId']['ClassData'])})
            logout.output_log_debug(self, '商品ID取得箇所:' + item_list_meta['ItemId']['ClassKey'] + item_list_meta['ItemId'][
                'ClassData'])

            # 商品名
            item_name_list = bf.find_all(
                attrs={item_list_meta['ItemName']['ClassKey']: re.compile(item_list_meta['ItemName']['ClassData'])})
            logout.output_log_debug(self,
                                    '商品名取得箇所:' + item_list_meta['ItemName']['ClassKey'] + item_list_meta['ItemName'][
                                        'ClassData'])

            logout.output_log_debug(self, '取得データ：' + str(item_id_list))
            logout.output_log_debug(self, '取得データ：' + str(item_name_list))

            item_id_text_list = []
            for item_id in item_id_list:
                item_id_text_list.append(item_id.text)

            item_name_text_list = []
            for name in item_name_list:
                item_name_text_list.append(name.text)

            item_dict = dict(zip(item_id_text_list, item_name_text_list))

        except Exception:
            logout.output_log_error(self, '出品商品一覧からデータの取得が失敗しました。')
            logout.output_log_error(self, traceback.format_exc())
            raise Exception('出品商品一覧からデータの取得が失敗しました。')

        return item_dict

    def get_sell_item_stock(self) -> list:
        """
        Returns:
            list: 商品ごとの現在色、サイズ、在庫の有無
        """
        try:
            item_stock_meta = self.meta['ItemOfInfo']['ItemStockInfo']

            # 出品リストのページへアクセス
            self.site_access.script_compile(input_url=item_stock_meta['ItemStockURL'])
            logout.output_log_debug(self, '出品サイトURL:' + item_stock_meta['ItemStockURL'])

            # 商品の在庫情報取得箇所指定用リスト
            item_dict = self.get_sells_item_list()
            logout.output_log_debug(self, '商品の内容:' + str(item_dict))

            # Buyma上の商品ウェジットの中の内容が入力されている
            buyma_item_list = []

            # 商品が存在し続ける間処理を続ける
            for item in item_dict.keys():
                logout.output_log_info(self, '対象商品ID : ' + item)
                logout.output_log_info(self, '対象商品名 : ' + item_dict.get(item))

                bf = BeautifulSoup(self.site_access.item_stock_change_button_click_for_buyma(item),
                                   'html.parser')

                stock_info = bf.select('#my > '
                                       'div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.fab-dialog--primary.cs-dialog > '
                                       'div.js-color-size-popup-box.fab-design-mg--t15.ui-dialog-content.ui-widget-content > '
                                       'div > '
                                       'div.js-size-input-wrap.color-size-color-wrap > '
                                       'table > '
                                       'tbody > '
                                       'tr')

                hedders = stock_info[0].find_all('th')
                hedder_text_list = []  # ヘッダー格納用リスト

                for hedder in hedders:
                    hedder_text_list.append(str(hedder.text).strip())

                # データ取得部
                item_row_list = []  # データ格納用リスト

                for data_row in stock_info:
                    row = []
                    for row_class in data_row.find_all(class_='fab-design-txtleft'):
                        if not row_class.find_all(attrs={'selected': True}):
                            row.append(row_class.text.strip())
                        else:
                            row.append(row_class.find(attrs={'selected': True}).text.strip())
                    item_row_list.append(row)

                # 取得対象データ
                logout.output_log_debug(self, str(item_row_list))

                # データ整形部
                # 商品のカラーリスト作成
                item_color = []
                for i in range(2, len(hedder_text_list), 1):
                    item_color.append(hedder_text_list[i])

                logout.output_log_debug(self, str(item_color))

                # 商品のサイズリスト作成
                item_size = []
                for row in item_row_list:
                    if row:
                        item_size.append(row[0])

                logout.output_log_debug(self, str(item_size))

                # 商品の有無フラグ
                item_existence = []
                # 行インデックス
                row_index = 0

                for row in item_row_list:
                    if row:
                        item_existence.append([])
                        for item_stock_existence_index in range(2, len(row), 1):
                            if row[item_stock_existence_index] == '買付可':
                                item_existence[row_index].append(Existence.IN_STOCK)
                            elif row[item_stock_existence_index] == '在庫なし':
                                item_existence[row_index].append(Existence.OUT_OF_STOCK)
                            elif row[item_stock_existence_index] == '手元に在庫あり':
                                item_existence[row_index].append(Existence.IN_STOCK_AT_HAND)
                            else:
                                item_existence[row_index].append(Existence.NO_INPUT)

                        row_index += 1

                logout.output_log_debug(self, str(item_existence))

                # 戻り値用の商品情報の作成
                buyma_item = BuymaItem(item_id=item, item_name=item_dict[item], item_info=[])
                for color_index, color in enumerate(item_color):
                    for size_index, size in enumerate(item_size):
                        buyma_item.item_info = ItemMeta(color=color,
                                                        size=size,
                                                        existence=item_existence[size_index][color_index])
                buyma_item_list.append(buyma_item)

            return buyma_item_list

        except Exception as e:
            message = 'Buymaの出品リスト商品の在庫状況データの取得が失敗しました。'
            logout.output_log_error(self, log_message=message, err=e)
            raise Exception(message)

    def get_item_id_list(self) -> list:
        """
        Buymaにて販売中の商品IDを全て取得する
        Returns:
            list: 商品IDリスト
        """
        item_id_list = []

        for buyma_item in self.__buyma_item_list:
            item_id_list.append(buyma_item.item_id)
        return item_id_list

    def get_item_color_list(self, item_id: str) -> list:
        """
        Buymaにて販売中の特定の商品IDの色を全て取得する
        Returns:
            list: 色リスト
        """
        item_color_list = []

        for buyma_item in self.__buyma_item_list:
            if buyma_item.item_id == item_id:
                for item_info in buyma_item.item_info:
                    item_color_list.append(item_info.color)

        return item_color_list

    def get_item_size_list(self, item_id: str, item_color: str) -> list:
        """
        Buymaにて販売中の特定の商品IDのサイズを全て取得する
        Returns:
            list: サイズリスト
        """
        item_size_list = []

        for buyma_item in self.__buyma_item_list:
            if buyma_item.item_id == item_id:
                for item_info in buyma_item.item_info:
                    if item_info.color == item_color:
                        item_size_list.append(item_info.size)

        return item_size_list

    def get_item_existence(self, item_id: str, item_color: str, item_size: str) -> Existence:
        """
        商品情報を受け取って在庫情報を返す
        Args:
            item_id: 商品ID
            item_color: 色
            item_size: サイズ

        Returns:
            Existence: 商品の在庫情報
        """
        for buyma_item in self.__buyma_item_list:
            if buyma_item.item_id == item_id:
                for item_info in buyma_item.item_info:
                    if item_info == ItemMeta(color=item_color, size=item_size):
                        return item_info.existence
        return Existence.NO_INPUT

    def input_item_stock(self, input_data: BuymaItem):
        """
        出品商品一覧から在庫情報の入力を行う
         Args:
             input_data(BuymaItem): 在庫情報を入力する商品
        """
        try:
            self.site_access.input_item_stock_for_buyma(input_data)
            self.update_item_info(input_data)
        except ItemIdException as err:
            raise err

    def close(self):
        """
        ブラウザの終了
        """
        self.site_access.exit()

    def update_item_info(self, buyma_item_for_update: BuymaItem):
        """
        商品情報を更新する
        Args:
            buyma_item_for_update(BuymaItem): 更新するBuyma上の商品
        """
        for buyma_item in self.__buyma_item_list:
            if buyma_item == buyma_item_for_update:
                for i, item_info in enumerate(buyma_item.item_info):
                    if item_info == buyma_item_for_update.item_info:
                        item_info[i] = buyma_item_for_update.item_info

    def check_item_stock_nothing(self) -> List:
        """
        Buyma上の商品が全て売り切れまたは在庫が1つでも存在する場合は出品の停止、復活をさせるため
        商品在庫が全て売り切れかどうか判定する
        Return:
            list: 商品ID,存在確認フラグの２次元配列(True 商品が一つでも存在しているもの, False 商品が全て存在しない商品)
        """
        item_id_list = list()
        exists_list = list()

        for buyma_item in self.__buyma_item_list:
            item_id_list.append(buyma_item.item_id)
            # 全ての商品に対して在庫が1つでも存在するか判定する
            item_info_for_existence = [item_info.existence for item_info in buyma_item.item_info]
            exists_list.append(any([existence == Existence.IN_STOCK or
                                    existence == Existence.IN_STOCK_AT_HAND for
                                    existence in item_info_for_existence]))

        stock_exists_list = [item_id_list, exists_list]

        return stock_exists_list

    def output_csv_nothing_stock(self):
        """
        商品が全て売り切れているものをCSVに出力する
        Returns:
            List(str): 売り切れている商品ID
        """
        item_stock_list = self.check_item_stock_nothing()

        # 商品が存在しないものをCSV出力する
        df = pd.DataFrame({'item_id': item_stock_list[0],
                           'item_exists': item_stock_list[1]})
        data_len = len(df[df.item_exists != Existence.OUT_OF_STOCK])
        if data_len > 0:
            df[df.item_exists == Existence.OUT_OF_STOCK].to_csv('output_data/stock_nothing_item.csv', index=False)
        else:
            logout.output_log_info(self, '出品停止対象の商品はありませんでした。')

        item_id_stock_nothing = list()

        for item_id in item_stock_list:
            if item_id:
                item_id_stock_nothing.append(item_id)

        return item_stock_list

    @property
    def buyma_item_list(self) -> List[BuymaItem]:
        return self.__buyma_item_list

    @buyma_item_list.setter
    def buyma_item_list(self, buyma_item):
        if isinstance(buyma_item, BuymaItem):
            self.__buyma_item_list.append(buyma_item)
        elif isinstance(buyma_item, list):
            if all(isinstance(item, BuymaItem) for item in buyma_item):
                self.__buyma_item_list = buyma_item
