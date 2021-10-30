from typing import Dict, List, Tuple

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from exception.exceptions import AppRuntimeException

from scrape.base_scraper import BaseScraper, ElementNotFoundException, scrape_retry

class IllegalURLException(AppRuntimeException):
    pass


class MrporterScraper(BaseScraper):

    def go_top_page(self) -> None:
        """ MrporterのTopページに移動する
        """
        pass


    def is_out_stock_all_size(self) -> bool:
        """ 在庫切れかを判断する

        Returns:
            bool: True（在庫なし）/ False（在庫あり）
        """

        try:
            # TODO　この条件で判定すると、urlをまちがえている場合でも在庫無しと判断されてしまう。
            is_sales = self.get_element_by_xpath_short_wait('//*[@aria-label="Add to Bag"]')
        except ElementNotFoundException:
            # Elementが見つからない　= 在庫切れ
            return True
        
        if is_sales:
           return False
        
        return True

    def get_stock_by_size(self, size: Dict) -> Tuple[Dict[str, bool], List[str]]:
        """ サイズごとの在庫の有無を取得する

        Args:
            size (Dict): 取得対象{'Mrporterのサイズ表記': 'Buymaのサイズ表記'}

        Returns:
            Tuple[Dict[str, bool], List[str]]: ({'Buymaのサイズ表記': '在庫の有無(True(有り)/False(無し))'}, 設定誤りのサイズリスト)
        """
        size_list = list(size.keys())
        if len(size_list) == 1 and size_list[0] == '':
            # アクセサリー等のsizeが無いもの処理
            try:
                self.get_element_by_xpath('//*[@aria-label="Add to Bag"]')
            except ElementNotFoundException:
                raise IllegalURLException('url_supplier mistake')
            
            return {list(size.values())[0]: True}, []

        try:
            elements = self.get_elements_by_xpath('//*[@class="GridSelect11__optionWrapper"]/label')
        except ElementNotFoundException:
            raise IllegalURLException('url_supplier mistake')
        
        # {'Mrporterのsize表記': '取得した在庫有無（True）'}

        mrporter_stock = {element.text: 'sold out' not in element.get_attribute('aria-label') for element in elements}

        stock = dict()

        mistake_size_list = list()
        for mrporter_size, buyma_size in size.items():
            is_stock = mrporter_stock.get(mrporter_size, None)
            
            if is_stock is None:
                # Mrporterから取得した在庫情報に設定したサイズが無い = 設定誤りとして検知
                mistake_size_list.append(mrporter_size)

            else:
                stock[buyma_size] = is_stock

        return stock, mistake_size_list

    @scrape_retry
    def go_item_page(self, url: str) -> None:
        self.driver.get(url)


    def run(self, url: str,  size: Dict[str, str]) -> Tuple[Dict[str, bool], List[str]]:
        """　Mrporterの在庫を取得する

        Args:
            url (str): Mrporterのurl
            size (Dict[str, str]): {Mrporterのサイズ表記: Buymaのサイズ表記}

        Returns:
            Tuple[Dict[str, bool], List[str]]: ({'Buymaのサイズ表記': '在庫の有無(True(有り)/False(無し))'}, 設定誤りのサイズリスト)
        """
        self.go_item_page(url)

        if self.is_out_stock_all_size():
            #　在庫切れの場合 = 全てのサイズFalse（在庫なし）
            return {buyma_size: False for buyma_size in size.values()}, list()

        stock,  mistake_size_list= self.get_stock_by_size(size)

        return stock, mistake_size_list
