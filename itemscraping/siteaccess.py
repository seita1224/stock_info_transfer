"""
サイトにアクセスして操作を行う場合の処理を集めたモジュール
Todo:
    サイト依存データをsitesmeta.pyから読み込む仕組みを組み込む
"""

import time
import traceback

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
import chromedriver_binary
from selenium.webdriver.common.action_chains import ActionChains
from itemscraping import sitesmeta
import logout
import re

from models import BuymaItem


class SiteAccess:
    """
    それぞれのサイトに依存するデータはsitesmeta.pyを使用し取得してくる
    """
    # ブラウザの保存
    DRIVER = None

    def __init__(self):
        """
        サイトアクセスの準備
        """
        # ブラウザのオプションを格納する変数をもらってきます。
        options = ChromeOptions()

        # ヘッドレスモードを有効にする（次の行をコメントアウトすると画面が表示される）。
        # options.add_argument('--headless')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/79.0.3945.88 Safari/537.36')

        # ChromeのWebDriverオブジェクトを作成する。
        self.DRIVER = Chrome(options=options)

        # 要素が見つかるまで繰り返し処理する時間
        self.DRIVER.implicitly_wait(10)

    def script_compile(self, input_url=None):
        """
        javascriptコンパイル済みのhtmlを返します。
        汎用的なメソッドとして残しておく
        Args:
            input_url (str):HTMLの取得を行うサイトのURL
        Returns:
            Union[int, list[Union[int,str]]]:javascriptがコンパイルされたHTML基本的には文字列が返されるイメージで良い
        """
        conf_url = input_url

        # インスタンスにて指定したサイトにアクセスする(アクセスしたタイミングでjavascriptがコンパイルされる)
        self.DRIVER.get(conf_url)

        # htmlを返す
        return self.DRIVER.page_source

    def script_compile_move(self, meta: dict):
        """
        javascriptコンパイル済みのhtmlを返します。
        サイト内でクリックなどの動作が必要になったタイミングで
        メタ情報を元に操作を行い必要なHTMLのみを返す
        Args:
            meta (dict<str:Union[int, list[Union[int,str], dict]>):設定ファイルないのメタ情報を渡す
        Returns:
            Union[int, list[Union[int,str]]],None:javascriptがコンパイルされたHTML基本的には文字列が返されるイメージで良い
        """
        # キー名にActionsが付いてない場合はこのメソッドを使用しない
        repattarn = re.compile('.*Actions.*')

        # 辞書型の1つめのキーに「Actions」を検知する
        if bool(repattarn.search(list(meta.keys())[0])):
            # 検知した結果各設定値のkeyの内容にそってブラウザを操作する
            for config_key in meta.keys():
                if config_key == 'Click':
                    pass
                elif config_key == 'Read':
                    pass
                elif config_key == 'Input':
                    pass
        else:
            return None

        # htmlを返す
        return self.DRIVER.page_source

    def login(self, site_meta: str):
        """
        サイトログインを行い遷移したいURLに遷移する
        Args:
            site_meta (str):設定ファイルの内容
        """
        site_meta = site_meta + '.LoginInfo'

        # メタ情報を読み込み
        try:
            meta = sitesmeta.SitesMeta()
            meta_info = meta.get_site_meta(data_names=site_meta)
            login_url = meta_info['URL']
            site_user_id = meta_info['ID']
            site_user_pw = meta_info['PW']
            id_css_selector = meta_info['IdCssSelector']
            pw_css_selector = meta_info['PwCssSelector']
            login_button_css_selector = meta_info['LoginButtonCssSelector']
        except Exception as e:
            raise e

        # ログイン先にアクセス
        self.DRIVER.get(login_url)

        # ID、PWの場所を指定して入力
        site_id = self.DRIVER.find_element_by_css_selector(id_css_selector)
        site_id.send_keys(site_user_id)
        site_pw = self.DRIVER.find_element_by_css_selector(pw_css_selector)
        site_pw.send_keys(site_user_pw)

        # 入力待ち
        time.sleep(1)

        # ログインボタンを指定しクリック
        login_button = self.DRIVER.find_element_by_css_selector(login_button_css_selector)
        login_button.click()

    def item_stock_change_button_click_for_buyma(self, click_meta_item):
        """
        Buyma専用メソッド
        商品一覧画面から編集ボタンを押したあとのHTMLを返す
        Returns:
            Union[int, list[Union[int,str]]],None:javascriptがコンパイルされたHTML基本的には文字列が返されるイメージで良い
        """
        page_source = None

        # 指定されたクラス名を全て取得
        logout.output_log_debug(self, '在庫情報の取得開始')

        click_items = self.DRIVER.find_elements_by_class_name('js-popup-color-size')
        for click_item in click_items:
            item_attr = click_item.get_attribute('data-syo-id')
            click_meta_item = click_meta_item.lstrip('0')
            # 取得したい商品ID(引数)と編集ボタンの商品IDが一致した場合ウィジットを開き処理を行う
            if item_attr == click_meta_item:
                # 商品情報ウィジットの開きソースの取得
                actions_open = ActionChains(self.DRIVER)
                actions_open.move_to_element(to_element=click_item)
                actions_open.click(on_element=click_item)
                actions_open.perform()
                time.sleep(1)
                page_source = self.DRIVER.page_source
                logout.output_log_debug(self, 'HTML取得完了')

                # 商品情報ウィジットを閉じる
                actions_close = ActionChains(self.DRIVER)
                wigit_close_button = self.DRIVER.find_elements_by_css_selector(
                    '#my > '
                    'div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.fab-dialog--primary.cs-dialog > '
                    'div.ui-dialog-titlebar.ui-widget-header.ui-corner-all.ui-helper-clearfix > '
                    'a')
                actions_close.move_to_element(to_element=wigit_close_button[0])
                actions_close.click(on_element=wigit_close_button[0])
                actions_close.perform()
                logout.output_log_debug(self, '商品情報ウィジットのクローズ')
                time.sleep(1)

        return page_source

    def input_item_stock_for_buyma(self, input_data: BuymaItem):
        """
        Buyma専用メソッド
        サイト内の特定の箇所に入力したいデータを入力する
        Args:
            input_data (BuymaItem):入力したいデータ
        """
        logout.output_log_debug('商品情報の入力')
        # 編集ボタンクリック
        logout.output_log_debug(self, '編集ボタンのxpath: //*[@data-vt="/vt/my/buyeritems/edit/colorsize/' + input_data.item_id + '"]')
        editButton = self.DRIVER.find_element_by_xpath('//*[@data-vt="/vt/my/buyeritems/edit/colorsize/' + input_data.item_id + '"]')
        logout.output_log_debug(self, str(editButton))
        editButton.click()

        self.DRIVER.refresh()

        # 色情報取得
        # 色情報ヘッダーの取得　
        logout.output_log_debug(self, '色ヘッダーxpath: //*[@id="my"]/div[10]/div[2]/div/div[1]/table/tbody/tr[1]/th')
        sorce = self.DRIVER.find_element_by_xpath('//*[@id="my"]')
        sorce = sorce.find_elements_by_xpath('/div[10]')
        logout.output_log_debug(self, sorce.text)

        sorce = self.DRIVER.find_element_by_xpath('//*[@id="my"]/div[10]/div[2]/div/div[1]/table')
        color_header = sorce.find_elements_by_xpath('.//th')

        logout.output_log_debug(self, color_header)
        logout.output_log_debug(self, '色ヘッダー取得内容:' + str(color_header))


        # 色情報のリストを作成
        logout.output_log_debug(self, '色ヘッダー取得内容:' + str(color_header))
        color_list = [v for i, v in enumerate(color_header) if i >= 2 and v is not None]

        # サイズ情報の取得
        logout.output_log_debug(self, 'サイズカラムxpath: //*[@id="my"]/div[10]/div[2]/div/div[1]/table/tbody/tr')
        size_column = self.DRIVER.find_elements_by_xpath('//*[@id="my"]/div[10]/div[2]/div/div[1]/table/tbody/tr')

        # サイズ情報のリストを作成
        logout.output_log_debug(self, 'サイズカラム取得内容: ' + str(size_column))
        size_list = size_column[[i for i in range(len(size_column))][0]]

        # 変更箇所の確定
        # 引数に設定された商品の色とリスト内(color_list)の色が一致した箇所の保存
        color_place_map = {}
        for i, color in enumerate(color_list):
            for item_info in input_data.item_info:
                if item_info.color == color:
                    color_place_map[color] = i

        # 引数に設定された商品のサイズとリスト内(size_list)のサイズが一致した箇所の保存
        size_place_map = {}
        for i,size in enumerate(size_list):
            for item_info in input_data.item_info:
                if item_info.size == size:
                    size_place_map[size] = size

        # 商品入力用のオブジェクト取得(Selenium上で商品の有無のリストボックスを操作できるよう取得)
        for item_info in input_data.item_info:
            item_inventory_list_box = \
                self.DRIVER.find_elements_by_xpath('//*[@id="my"]/div[10]/div[2]/div/div[1]/table/tbody/'
                                               'tr[' + size_place_map[item_info.size] + ']/'
                                               'td['+ color_place_map[item_info.color] +']/div/select/')

        # ここで商品の各リストボックスを扱う
        for item_inventory in item_inventory_list_box:
            item_inventory.is_selected()



    def read(self):
        """
        サイト内の内容を読み取り読み取った箇所のHTMLを返す
        Returns:
            Union[int, list[Union[int,str]]],None:javascriptがコンパイルされたHTML基本的には文字列が返されるイメージで良い
        """
        pass

    def input(self, input_data):
        """
        サイト内の特定の箇所に入力したいデータを入力する
        Args:
            input_data (str):入力したいデータ
        """
        pass

    def exit(self):
        """
            ブラウザの終了
        """
        self.DRIVER.quit()
