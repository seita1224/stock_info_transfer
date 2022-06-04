from typing import Dict, List, Tuple

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from exception.exceptions import AppRuntimeException

from scrape.base_scraper import BaseScraper, ElementNotFoundException, scrape_retry

class IllegalURLException(AppRuntimeException):
    pass


class FarfetchScraper(BaseScraper):
    
    def get_elements_by_xpath(self, xpath: str) -> List[WebElement]:
        """ オーバーライド
        """
        try:
            elements = self.driver.find_elements_by_xpath(xpath)
        except TimeoutException:
            # TODO 適切なメッセージの検討
            raise ElementNotFoundException(f'xpath: {xpath}')

        return elements

    def go_top_page(self) -> None:
        """ farfetchのTopページに移動する
        """
        pass


    def is_out_stock_all_size(self) -> bool:
        """ 在庫切れかを判断する

        Returns:
            bool: True（在庫なし）/ False（在庫あり）
        """

        try:
            out_stock = self.get_element_by_xpath_short_wait('//*[@data-tstid="addToBag"]')
        except ElementNotFoundException:
            # Elementが見つからない　= 在庫切れではない
            return True
        
        if not out_stock:
           return True
        
        return False

    def get_stock_by_size(self, size: Dict) -> Tuple[Dict[str, bool], List[str]]:
        """ サイズごとの在庫の有無を取得する

        Args:
            size (Dict): 取得対象{'Farfetchのサイズ表記': 'Buymaのサイズ表記'}

        Returns:
            Tuple[Dict[str, bool], List[str]]: ({'Buymaのサイズ表記': '在庫の有無(True(有り)/False(無し))'}, 設定誤りのサイズリスト)
        """
        size_list = list(size.keys())
        if len(size_list) == 1 and size_list[0] == '':
            # アクセサリー等のsizeが無いもの処理
            try:
                self.get_element_by_xpath('//*[@data-tstid="addToBag"]')
            except ElementNotFoundException:
                raise IllegalURLException('url_supplier mistake from farfetch')
            
            return {list(size.values())[0]: True}, []
        try:
            elements = self.get_elements_by_xpath('//*[@data-tstid="productOffer"]/*[@id="sizesDropdown"]/div/div/div/div/span/span[@data-tstid="sizeDescription"]')
        except ElementNotFoundException:
            raise IllegalURLException('url_supplier mistake from farfetch')
        
        # {'Farfetchのsize表記': '取得した在庫有無（True）'}
        # span要素は'text'で取得できないため、get_attribute("textContent")で取得
        farfetch_stock = {element.get_attribute("textContent"): bool(element.is_enabled()) for element in elements}
        print(farfetch_stock)
        stock = dict()

        mistake_size_list = list()
        for farfetch_size, buyma_size in size.items():
            is_stock = farfetch_stock.get(farfetch_size, None)
            
            if is_stock is None:
                # Farfetchから取得した在庫情報に設定したサイズが無い = 設定誤りとして検知
                mistake_size_list.append(farfetch_size)

            else:
                stock[buyma_size] = is_stock

        return stock, mistake_size_list

    @scrape_retry
    def go_item_page(self, url: str) -> None:
        self.driver.get(url)


    def run(self, url: str,  size: Dict[str, str]) -> Tuple[Dict[str, bool], List[str]]:
        """ Farfetchの在庫を取得する

        Args:
            url (str): Farfetchのurl
            size (Dict[str, str]): {Farfetchのサイズ表記: Buymaのサイズ表記}

        Returns:
            Tuple[Dict[str, bool], List[str]]: ({'Buymaのサイズ表記': '在庫の有無(True(有り)/False(無し))'}, 設定誤りのサイズリスト)
        """
        self.go_item_page(url)

        if self.is_out_stock_all_size():
            #　在庫切れの場合 = 全てのサイズFalse（在庫なし）
            return {buyma_size: False for buyma_size in size.values()}, list()

        stock,  mistake_size_list= self.get_stock_by_size(size)

        return stock, mistake_size_list
