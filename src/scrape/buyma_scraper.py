from datetime import date
import time
from typing import Dict, List
import re

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from exception.exceptions import AppRuntimeException
from scrape.base_scraper import BaseScraper, ElementNotFoundException, scrape_retry

from setting import settings
from utils import calc_date

class BuymaIdNotFoundException(AppRuntimeException):
    pass

class BuymaColorNotFundException(AppRuntimeException):
    pass

class BuymaScraper(BaseScraper):

    is_first_access = False

    @scrape_retry
    def go_item_manege_page(self) -> None:
        """ 在庫管理ページに移動
        """
        self.driver.get('https://www.buyma.com/my/sell/?page=1&tab=b#/')
        
        if not self.is_first_access:
            self.get_element_by_xpath('//*[@id="row-count-options"]').click()
            self.get_element_by_xpath('//*[@id="row-count-options"]/option[3]').click()

            self.is_first_access = True

    @scrape_retry
    def login(self) -> None:
        """ buymaにログインする

        Args:
            id (str): ログインID
            password (str): パスワード
        """
        self.driver.get('https://www.buyma.com/login/')
        # seleniumでログインを行うとエラーとなることが
        # 頻発するため、手動でのログインを促す。
        input('buymaへログインした後にEnterを押してください。')

    def __go_next_page(self) -> bool:
        """ 次の在庫管理ページに移動する

        Returns:
            bool: 次へボタンの有無(True（有り）/ False(無し))
        """
        try:
            next_button = self.get_element_by_xpath_short_wait('//*[@rel="next"]')
            next_button.click()
            return True
        except ElementNotFoundException:
            return False 

    def go_item_edhit_page(self, buyma_id: str) -> WebElement:
        """ 在庫編集画面に移動する

        Args:
            buyma_id (str): 編集するbuymaの商品id

        Returns:
            編集ボタン: 一致するbuymaの商品idが無い場合、None
        """
        while True:
            try:
                edhit_button = self.get_element_by_xpath_short_wait(f'//*[@class="js_item_colorsize_edit"]/*[@data-syo-id="{buyma_id}"]')
                return edhit_button
            except ElementNotFoundException:
                if not self.__go_next_page():
                    return None
    
    def change_max_seles_count(self, max_seles_count: str) -> bool:
        """ 買付可能数の変更

        Args:
            max_seles_count (str): 設定する買付可能数

        Returns:
            bool: 買い付け可能数の変更完了の是非(True/False(変更できなかった。（出品停止処理が必要）)) 
        """
        max_seles_element = self.get_element_by_xpath_short_wait('//*[@class="js-colorsize-capacity-amount sell-unit-summary-input"]')

        # 対象の商品が全て在庫なしの場合、非活性のため入力しない
        if max_seles_element.is_enabled():
            max_seles_element.clear()
            max_seles_element.send_keys(max_seles_count)

            return True

        else:
            # 手元に在庫があるかをチェックし、なければ在庫なし=Trueを返す。
            is_stock = self.get_element_by_xpath_short_wait('//*[@class="js-colorsize-unit-summary"]')
            
            if is_stock.text == '0':
                return False
            else:
                # 買い付け先に在庫無しでも、手元に在庫ありの場合は、
                # 出品停止にしない（在庫あり）ため、Trueを返す。
                return True


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
                selected = self.get_element_by_xpath_short_wait(select_xpath + '/option[@selected]')
            except ElementNotFoundException:
                # サイズの設定ミスの場合、ここでエラーとなる
                mistake_size_list.append(buyma_size)
                continue
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
        TODO 処理の改善（スマートにしたい）
        """
        save_button = self.get_element_by_xpath('//*[@class="js-commit-changes fab-button fab-button--primary fab-button--m"]')
        save_button.click()
        time.sleep(2)

        try:
            error_message = self.get_element_by_xpath_short_wait('//*[@class="error js-error-messasge-area"]')
        except ElementNotFoundException:
                # エラーが取得できない場合は、正常に保存が行えているため、処理終了する。
                return

        if not error_message.text == '':
            try:
                cansel_button = self.get_element_by_xpath_short_wait('//*[@class="js-close-popup fab-button fab-button--back fab-button--m"]')
                cansel_button.click()
                time.sleep(2)
            except ElementNotFoundException:
                return

    def is_now_sales(self, item_id: str):
        
        status = self.get_element_by_xpath_short_wait(f'//*[@id="_item_edit_status_{item_id}"]')
        str_status = status.get_attribute('data-item-edit-status')
        if str_status == 'Sts01':
            #出品中
            return True
        if str_status == 'Sts04':
            return False

    def change_status(self, item_id: str, code: int):
        """ 出品停止・再開を行う

        Args:
            item_id (str): 対象のbuyma_id
            code (int): 1(出品再開)/2(出品停止)
        """
        change_status_page = self.get_element_by_xpath(f'//*[@data-vt="/vt/my/buyeritems/item_name/{item_id}"]')
        change_status_page.click()
        time.sleep(2)

        if code == 1:
            # 出品再開
            switch_button = self.get_element_by_xpath('//*[@class="bmm-c-switch sell-status-switch"]')
        elif code == 2:
            # 出品停止
            switch_button = self.get_element_by_xpath('//*[@class="bmm-c-switch is-checked sell-status-switch"]')
        
        # 要素がラベルのため、click()メソッドが使用できないため、
        # スクリプトを実行させクリック処理を実施。
        self.driver.execute_script("arguments[0].click();", switch_button)

        time.sleep(1)
        change_status = self.get_element_by_xpath('//*/button')
        change_status.click()
        
        while True:
            time.sleep(2)
            cur_url = self.driver.current_url
            if cur_url == 'https://www.buyma.com/my/sell/completed':
                break
    
    def extend_sales_period(self, buyma_id: str):
        """ 販売期間の延長する
        
        Args:
            buyma_id (str): 対象のbuyma商品ID
        """
        extend_days = calc_date.plus_weeks_from_today(int(settings.extension_sales_week))
        edit_button = self.get_element_by_xpath_short_wait(f'//*[@data-vt="/vt/my/buyeritems/edit/date/{buyma_id}"]')
        # edit_button.click()
        self.driver.execute_script("arguments[0].click();", edit_button)
        time.sleep(1)
        while True:
            calendar_year = self.get_element_by_xpath_short_wait('//*[@class="ui-datepicker-year"]')
            calendar_month = self.get_element_by_xpath_short_wait('//*[@class="ui-datepicker-month"]')
            
            calendar_date = date(
                int(re.sub(r'\D', '', calendar_year.text)),
                int(re.sub(r'\D', '', calendar_month.text)),
                1
            )
            if calendar_date < extend_days.replace(day=1):
                self.get_element_by_xpath_short_wait('//*[@class="ui-datepicker-next ui-corner-all"]').click()
            else:
                self.get_element_by_xpath_short_wait(f'//*[@class="ui-datepicker-calendar"]/tbody/tr/td/a[text()="{extend_days.day}"]').click()
                time.sleep(2)
                break

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
        
        ehit_item_button = self.go_item_edhit_page(buyma_id)
        if ehit_item_button is None:
            # 次ページに行けなかった = 設定したbuyma_idが在庫管理に存在しない
            raise BuymaIdNotFoundException('buyma_id mistake')
        
        self.driver.execute_script("arguments[0].click();", ehit_item_button)
        # 商品が出品中なのかを取得する。
        is_sales = self.is_now_sales(buyma_id)

        mistake_size_list = self.change_stock(color, stock_data)
        is_stock = self.change_max_seles_count(settings.buyma_max_sales_count)
        # 販売期間の延長
        self.save_change_stock()
        self.extend_sales_period(buyma_id)
        if is_stock:
            if is_sales == False:
                #在庫あるが、出品停止中の場合、出品再開処理をおこなう。
                self.change_status(buyma_id, 1)
                print(f'buyma_id={buyma_id}を出品再開しました。')
        else:
            if is_sales:
                #在庫無しだが、出品中の場合、出品停止処理をおこなう。
                self.change_status(buyma_id, 2)
                print(f'buyma_id={buyma_id}を出品停止しました。')
        
        if is_sales is None:
            print(f'buyma_id={buyma_id}のステータスが「出品中/出品停止中」以外になっています。')

        return mistake_size_list
