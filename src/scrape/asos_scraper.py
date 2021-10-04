from typing import Dict, List, Tuple

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from exception.exceptions import AppRuntimeException

from scrape.base_scraper import BaseScraper, ElementNotFoundException, scrape_retry

class IllegalURLException(AppRuntimeException):
    pass


class AsosScraper(BaseScraper):

    def go_top_page(self) -> None:
        """ AsosのTopページに移動する
        """
        self.driver.get('https://www.asos.com/')

    def is_out_stock_all_size(self) -> bool:
        """ 在庫切れかを判断する

        Returns:
            bool: True（在庫なし）/ False（在庫あり）
        """

        try:
            out_stock = self.get_element_by_xpath_short_wait('//*[@class="product-out-of-stock-label"][text()="Out of stock"]')
        except ElementNotFoundException:
            # Elementが見つからない　= 在庫切れではない
            return False
        
        if out_stock:
           return True
        
        return False

    def get_stock_by_size(self, size: Dict) -> Tuple[Dict[str, bool], List[str]]:
        """ サイズごとの在庫の有無を取得する

        Args:
            size (Dict): 取得対象{'Asosのサイズ表記': 'Buymaのサイズ表記'}

        Returns:
            Tuple[Dict[str, bool], List[str]]: ({'Buymaのサイズ表記': '在庫の有無(True(有り)/False(無し))'}, 設定誤りのサイズリスト)
        """
        size_list = list(size.keys())
        if len(size_list) == 1 and size_list[0] == '':
            # アクセサリー等のsizeが無いもの処理
            try:
                self.get_element_by_xpath('//*[@aria-label="Add to bag"]')
            except ElementNotFoundException:
                raise IllegalURLException('url_supplier mistake')
            
            return {list(size.values())[0]: True}, []

        try:
            elements = self.get_elements_by_xpath('//*[@id="main-size-select-0"]/option')
        except ElementNotFoundException:
            raise IllegalURLException('url_supplier mistake')
        
        # {'Asosのsize表記': '取得した在庫有無（True）'}
        asos_stock = {element.text.split(' - ')[0]: bool(element.is_enabled()) for element in elements}

        stock = dict()

        mistake_size_list = list()
        for asos_size, buyma_size in size.items():
            is_stock = asos_stock.get(asos_size.split(' - ')[0], None)
            
            if is_stock is None:
                # Asosから取得した在庫情報に設定したサイズが無い = 設定誤りとして検知
                mistake_size_list.append(asos_size)

            else:
                stock[buyma_size] = is_stock

        return stock, mistake_size_list

    @scrape_retry
    def go_item_page(self, url: str) -> None:
        self.driver.get(url)


    def run(self, url: str,  size: Dict[str, str]) -> Tuple[Dict[str, bool], List[str]]:
        """　Asosの在庫を取得する

        Args:
            url (str): Asosのurl
            size (Dict[str, str]): {Asosのサイズ表記: Buymaのサイズ表記}

        Returns:
            Tuple[Dict[str, bool], List[str]]: ({'Buymaのサイズ表記': '在庫の有無(True(有り)/False(無し))'}, 設定誤りのサイズリスト)
        """
        self.go_item_page(url)

        if self.is_out_stock_all_size():
            #　在庫切れの場合 = 全てのサイズFalse（在庫なし）
            return {buyma_size: False for buyma_size in size.values()}, list()

        stock,  mistake_size_list= self.get_stock_by_size(size)

        return stock, mistake_size_list
