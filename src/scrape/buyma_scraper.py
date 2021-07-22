import re
from typing import Dict, List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from soupsieve import select
from exception.exceptions import AppRuntimeException
from scrape.base_scraper import BaseScraper, ElementNotFoundException, scrape_retry

from setting import settings

class BuymaIdNotFoundException(AppRuntimeException):
    pass

class BuymaColorNotFundException(AppRuntimeException):
    pass

class BuymaScraper(BaseScraper):

    @scrape_retry
    def go_item_manege_page(self) -> None:
        """ 在庫管理ページに移動
        """
        self.driver.get('https://www.buyma.com/my/sell/?page=1&tab=b#/')
        self.get_element_by_xpath('//*[@id="row-count-options"]').click()
        self.get_element_by_xpath('//*[@id="row-count-options"]/option[3]').click()

    @scrape_retry
    def login(self) -> None:
        """ buymaにログインする

        Args:
            id (str): ログインID
            password (str): パスワード
        """
        self.driver.get('https://www.buyma.com/login/')
        # TODO seleniumでログインを行うとエラーとなることが
        # 頻発するため、手動でのログインを促す。
        input('buymaへログインした後にEnterを押してください。')

    def __go_next_page(self) -> bool:
        """ 次の在庫管理ページに移動する

        Returns:
            bool: 次へボタンの有無(True（有り）/ False(無し))
        """
        try:
            next_button = self.get_element_by_xpath('//*[@rel="next"]')
            next_button.click()
            return True
        except ElementNotFoundException:
            return False 

    def go_item_edhit_page(self, buyma_id: str) -> bool:
        """ 在庫編集画面に移動する

        Args:
            buyma_id (str): 編集するbuymaの商品id

        Returns:
            bool: 現在のページに一致するbuymaの商品idが無い場合、False
        """
        try:
            edhit_button = self.get_element_by_xpath(f'//*[@class="js_item_colorsize_edit"]/*[@data-syo-id="{buyma_id}"]')
            edhit_button.click()
            return True
        except ElementNotFoundException:
            return False
    
    def change_max_seles_count(self, max_seles_count: str):
        """ 買付可能数の変更

        Args:
            max_seles_count (str): 設定する買付可能数
        """
        max_seles_element = self.get_element_by_xpath('//*[@class="js-colorsize-capacity-amount sell-unit-summary-input"]')

        # 対象の商品が全て在庫なしの場合、非活性のため入力しない
        if max_seles_element.is_enabled:
            max_seles_element.clear()
            max_seles_element.send_keys(max_seles_count)


    def change_stock(self, color: str, stock_data: Dict[str, bool]) -> List[str]:
        """ 在庫編集処理

        Args:
            color (str): 編集対象のcolor名
            stock_data (Dict[str, bool]): 仕入れ先から取得した在庫情報
                {"buymaのサイズ表記": "在庫有無（True(有)/False(無)）"}

        Raises:
            BuymaColorNotFundException: 引数のcolorが編集画面に無い場合に発生
        """
        
        # テーブルヘッダーの色情報を取得し、編集対象の列を特定する
        color_headers = self.get_elements_by_xpath('//*[@class="csp-table-color"]')
        for color_location, color_header in enumerate(color_headers, 1):
            if color_header.text == color:
                target_position_num = color_location
                break
        else:
            raise BuymaColorNotFundException(f'color_info_buyma mistake')

        # 在庫編集処理
        mistake_size_list = []
        for buyma_size, is_stock in stock_data.items():
            select_xpath = f'//*[@class="fab-design-txtleft"][text()="{buyma_size}"]/following-sibling::node()\
                [@class="fab-design-txtleft fab-form"][{target_position_num}][1]/*/select'

            # 手元に在庫ありが選択されている場合は編集しない
            try:
                selected = self.get_element_by_xpath(select_xpath + '/option[@selected]')
            except ElementNotFoundException:
                # サイズの設定ミスの場合、ここでエラーとなる
                mistake_size_list.append(buyma_size)
            
            if selected.get_attribute('value') == "2":
                continue

            select_element = self.get_element_by_xpath(select_xpath)
            select_element.click()
            select = Select(select_element)

            if is_stock:
                # 買付可
                select.select_by_value("1")
            else:
                # 在庫なし
                select.select_by_value("0")

        return mistake_size_list
    
    def save_change_stock(self):
        """　編集画面の保存処理
        """
        save_button = self.get_element_by_xpath('//*[@class="js-commit-changes fab-button fab-button--primary fab-button--m"]')
        save_button.click()

        # TODO すべて在庫無しで更新ボタンを押すとエラーになるため、
        # それを判断し、後続の出品停止処理につなげる。



    def run(self, buyma_id: str, color: str, stock_data: Dict[str, bool]) -> List[str]:
        """ 実行処理

        Args:
            buyma_id (str): 対象のbuymaの商品ID
            color (str): 対象のカラー情報
            stock_data (Dict[str, bool]): 仕入れ先から取得した在庫情報

        Raises:
            BuymaIdNotFoundException: 対象のBuyma idが管理画面に存在しないしない場合エラー

        Returns:
            List[str]: 設定ミスのサイズリスト
        """
        self.go_item_manege_page()
        
        while not self.go_item_edhit_page(buyma_id):

            if not self.__go_next_page():
                # 次ページに行けなかった = 設定したbuyma_idが在庫管理に存在しない
                raise BuymaIdNotFoundException('buyma_id mistake')

        mistake_size_list = self.change_stock(color, stock_data)
        self.change_max_seles_count(settings.buyma_max_sales_count)
        self.save_change_stock()
        # TODO 出品停止処理の実装/出品再開処理も
