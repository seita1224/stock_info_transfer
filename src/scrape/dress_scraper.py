from typing import Dict, List, Tuple
from numpy import e

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from exception.exceptions import AppRuntimeException

from scrape.base_scraper import BaseScraper, ElementNotFoundException, scrape_retry

class IllegalURLException(AppRuntimeException):
    pass


class DressScraper(BaseScraper):

    def go_top_page(self) -> None:
        """ dressのTopページに移動する
        """
        self.driver.get('https://www.dressinn.com/')

    def is_out_stock_all_size(self) -> bool:
        """ 在庫切れかを判断する

        Returns:
            bool: True（在庫なし）/ False（在庫あり）
        """

        try:
            out_stock = self.get_element_by_xpath_short_wait('//*[@class="titulo_descatalogados"]')
        except ElementNotFoundException:
            # Elementが見つからない　= 在庫切れではない
            return False
        
        if out_stock:
           return True
        
        return False

    def get_stock_by_size(self, size: Dict) -> Tuple[Dict[str, bool], List[str]]:
        """ サイズごとの在庫の有無を取得する

        Args:
            size (Dict): 取得対象{'dressのサイズ表記': 'Buymaのサイズ表記'}

        Returns:
            Tuple[Dict[str, bool], List[str]]: ({'Buymaのサイズ表記': '在庫の有無(True(有り)/False(無し))'}, 設定誤りのサイズリスト)
        """
        size_list = list(size.keys())
        if len(size_list) == 1 and size_list[0] == '':
            # アクセサリー等のsizeが無いもの処理
            try:
                self.get_element_by_xpath('//*[@id="añadir_cesta"]')
            except ElementNotFoundException:
                raise IllegalURLException('url_supplier mistake from dress')
            
            return {list(size.values())[0]: True}, []

        try:
            elements = self.get_elements_by_xpath('//*[@id="tallas_detalle"]/option[text()]')
        except ElementNotFoundException:
            raise IllegalURLException('url_supplier mistake from dress')
        
        # {'dressのsize表記': '取得した在庫有無（True）'}
        dress_stock = {element.text.split(' / ')[0]: bool(element.is_enabled()) for element in elements}

        stock = dict()

        mistake_size_list = list()
        for dress_size, buyma_size in size.items():

            is_stock = dress_stock.get(dress_size.split(' / ')[0], False)
            stock[buyma_size] = is_stock

        return stock, mistake_size_list

    @scrape_retry
    def go_item_page(self, url: str) -> None:
        self.driver.get(url)


    def run(self, url: str,  size: Dict[str, str]) -> Tuple[Dict[str, bool], List[str]]:
        """　dressの在庫を取得する

        Args:
            url (str): dressのurl
            size (Dict[str, str]): {dressのサイズ表記: Buymaのサイズ表記}

        Returns:
            Tuple[Dict[str, bool], List[str]]: ({'Buymaのサイズ表記': '在庫の有無(True(有り)/False(無し))'}, 設定誤りのサイズリスト)
        """
        self.go_item_page(url)

        if self.is_out_stock_all_size():
            #　在庫切れの場合 = 全てのサイズFalse（在庫なし）
            return {buyma_size: False for buyma_size in size.values()}, list()

        stock,  mistake_size_list= self.get_stock_by_size(size)

        return stock, mistake_size_list
