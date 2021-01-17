"""
サイトにアクセスして操作を行う場合の処理を集めたモジュール
Todo:
    サイト依存データをsitesmeta.pyから読み込む仕組みを組み込む
"""
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
import chromedriver_binary
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from itemscraping import sitesmeta
import logout
import re

from models.existence import Existence
from models import BuymaItem


class SiteAccess:
    """
    それぞれのサイトに依存するデータはsitesmeta.pyを使用し取得してくる
    """
    # ブラウザの保存
    DRIVER = None

    # サイトアクセス処理リトライ回数
    __RETRIES = 5

    # 接続処理のタイムアウト時間
    __TIMEOUT_VERY_SHOT = 3
    __TIMEOUT_SHOT = 5
    __TIMEOUT_MIDDLE = 10
    __TIMEOUT_LONG = 20

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

        # ウィンドウの最大化
        self.DRIVER.maximize_window()

        # 要素が見つかるまで繰り返し処理する時間(second)
        self.DRIVER.implicitly_wait(self.__TIMEOUT_VERY_SHOT)

        # ページの読み込みが完了するまでの待機時間(second)
        self.DRIVER.set_page_load_timeout(self.__TIMEOUT_LONG)

        # ページのjavascriptが実行し終わるまでの待機時間(second)
        self.DRIVER.set_script_timeout(self.__TIMEOUT_LONG)

    def script_compile(self, input_url=None, obj=None):
        """
        javascriptコンパイル済みのhtmlを返します。
        汎用的なメソッドとして残しておく
        Args:
            input_url (str):HTMLの取得を行うサイトのURL
            obj (object): 呼び出し元のオブジェクト
        Returns:
            Union[int, list[Union[int,str]]]:javascriptがコンパイルされたHTML基本的には文字列が返されるイメージで良い
        """
        # Asosから呼び出された場合に稼働する
        if obj.__class__.__name__ == 'Asos':
            # ASOSの商品ページに飛ぶ前に一度トップページにアクセスする(サイトの仕様上直接商品ページへ飛べない仕様になっている)
            self.DRIVER.get('https://www.asos.com/')

            time.sleep(self.__TIMEOUT_VERY_SHOT)

            # アクセスが失敗した場合にリトライを行う
            retry = 0
            error = None
            while retry < self.__RETRIES:
                try:
                    logout.output_log_info(self, 'Asos商品ページアクセス処理開始')

                    # 商品ページへアクセス
                    self.DRIVER.get(input_url)

                    # 商品情報が読み込まれるまで待機
                    WebDriverWait(self.DRIVER, self.__TIMEOUT_VERY_SHOT).until(EC.visibility_of_all_elements_located)
                    time.sleep(self.__TIMEOUT_VERY_SHOT)

                except TimeoutException as te:
                    retry += 1
                    logout.output_log_warning(self, 'Asos商品ページアクセス処理失敗　再実行します')
                    error = te
                    # 商品ページへアクセス
                    self.DRIVER.get(input_url)
                    WebDriverWait(self.DRIVER, self.__TIMEOUT_MIDDLE).until(EC.visibility_of_all_elements_located)
                    continue
                else:
                    logout.output_log_info(self, 'Asos商品ページアクセス処理成功')
                    break
            else:
                logout.output_log_warning(self, log_message='Asos商品ページアクセス処理失敗: 商品が売り切れている可能性があります')
                logout.output_log_error(self, log_message='エラーの内容', err=error)
                raise error
        else:
            # アクセスが失敗した場合にリトライを行う
            retry = 0
            error = None
            while retry < self.__RETRIES:
                try:
                    # インスタンスにて指定したサイトにアクセスする(アクセスしたタイミングでjavascriptがコンパイルされる)
                    self.DRIVER.get(input_url)
                except TimeoutException as te:
                    retry += 1
                    error = te

                    # インスタンスにて指定したサイトにアクセスする(アクセスしたタイミングでjavascriptがコンパイルされる)
                    self.DRIVER.get(input_url)
                    WebDriverWait(self.DRIVER, self.__TIMEOUT_MIDDLE).until(EC.visibility_of_all_elements_located)
                    continue
                else:
                    logout.output_log_info(self, 'Asos商品ページアクセス処理成功')
                    break
            else:
                logout.output_log_error(self, log_message='エラーの内容', err=error)
                raise error

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

        # アクセスが失敗した場合にリトライを行う
        retry = 0
        error = None
        while retry < self.__RETRIES:
            try:
                logout.output_log_info(self, 'Buymaログイン処理開始')
                # ログイン先にアクセス
                self.DRIVER.get(login_url)

                # ID、PWの場所を指定して入力
                site_id = WebDriverWait(self.DRIVER, self.__TIMEOUT_VERY_SHOT).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, id_css_selector))
                )
                site_id.send_keys(site_user_id)

                site_pw = WebDriverWait(self.DRIVER, self.__TIMEOUT_VERY_SHOT).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, pw_css_selector))
                )
                site_pw.send_keys(site_user_pw)

                # ログインボタンを指定しクリック
                login_button = WebDriverWait(self.DRIVER, self.__TIMEOUT_VERY_SHOT).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, login_button_css_selector))
                )
                login_button.click()
            except TimeoutException as te:
                retry += 1
                logout.output_log_warning(self, 'ログイン処理失敗　再実行します')
                error = te
                continue

            else:
                logout.output_log_info(self, 'Buymaにログイン成功')
                break
        else:
            logout.output_log_error(self, log_message='ログイン処理失敗', err=error)
            raise error

    def item_stock_change_button_click_for_buyma(self, item_id):
        """
        Buyma専用メソッド
        商品一覧画面から編集ボタンを押したあとのHTMLを返す
        Args:
            item_id(str): 商品ID
        Returns:
            Union[int, list[Union[int,str]]],None: javascriptがコンパイルされたHTMLの文字列が返される
        """
        page_source = None

        # アクセスが失敗した場合にリトライを行う
        retry = 0
        error = None
        while retry < self.__RETRIES:
            try:
                logout.output_log_debug(self, '在庫情報取得処理開始')
                # 編集ボタンが表示されるまでの待機処理
                WebDriverWait(self.DRIVER, self.__TIMEOUT_VERY_SHOT).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'js-popup-color-size'))
                )

                click_items = self.DRIVER.find_elements_by_class_name('js-popup-color-size')
                for click_item in click_items:
                    item_attr = click_item.get_attribute('data-syo-id')
                    # 取得したい商品ID(引数)と編集ボタンの商品IDが一致した場合ウィジットを開き処理を行う
                    # 商品IDの左側に0が存在する場合は取り除く
                    if item_attr == item_id.lstrip('0'):
                        # 商品情報ウィジットの開きソースの取得
                        actions_open = ActionChains(self.DRIVER)
                        actions_open.move_to_element(to_element=click_item)
                        actions_open.click(on_element=click_item)
                        actions_open.perform()

                        if not 0 < retry:
                            time.sleep(self.__TIMEOUT_VERY_SHOT)
                        else:
                            time.sleep(self.__TIMEOUT_SHOT)

                        # 商品ページのHTMLの取得
                        page_source = self.DRIVER.page_source

                        WebDriverWait(self.DRIVER, self.__TIMEOUT_VERY_SHOT).until(
                            EC.visibility_of_element_located((By.XPATH, '/html/body/div[8]/div[1]/a'))
                        )

                        # 商品情報ウィジットを閉じる
                        actions_close = ActionChains(self.DRIVER)
                        wigit_close_button = self.DRIVER.find_element_by_xpath('/html/body/div[8]/div[1]/a')
                        actions_close.move_to_element(to_element=wigit_close_button)
                        actions_close.click(on_element=wigit_close_button)
                        actions_close.perform()

            except TimeoutException as te:
                retry += 1
                logout.output_log_warning(self, '在庫情報取得処理失敗　再実行します : リトライ回数:' + str(retry) +
                                                '  商品ID : ' + item_id)
                error = te
                continue

            else:
                logout.output_log_info(self, '在庫情報取得処理成功')
                break
        else:
            logout.output_log_error(self, log_message='在庫情報取得処理失敗', err=error)
            raise error

        return page_source

    def input_item_stock_for_buyma(self, input_data: BuymaItem):
        """
        Buyma専用メソッド
        サイト内の特定の箇所に入力したいデータを入力する
        Args:
            input_data (BuymaItem):入力したいデータ
        """
        logout.output_log_debug('商品情報の入力開始')

        # ブラウザがどんな状態でも商品リストのトップページへ遷移する
        self.first_page_access()

        # 商品の表示数を20件⇨100件へ変更する
        self.change_display_matter()

        # 編集ボタンクリック
        logout.output_log_debug(self,
                                '編集ボタンのxpath: //*[@data-vt="/vt/my/buyeritems/edit/colorsize/'
                                + input_data.item_id_nothing_zero + '"]')

        while True:
            change_button = self.DRIVER.find_elements_by_xpath(
                '//*[@data-vt="/vt/my/buyeritems/edit/colorsize/' + input_data.item_id_nothing_zero + '"]')

            # 変更対象の商品が存在しない場合は次へボタンをクリックする
            if not change_button:
                self.click_next_button()
                continue
            else:
                # 変更対象の商品が存在した場合は商品の入力処理を行う
                change_button = change_button[0]
                actions_open = ActionChains(self.DRIVER)
                actions_open.move_to_element(to_element=change_button)
                actions_open.click(on_element=change_button)
                actions_open.perform()

                # テスト用
                # image_dir = '/Users/seita/Program/python/stock_info_transfer/test_image/before_input.png'
                # self.DRIVER.save_screenshot(image_dir)

                # 商品の買い付けできる合計数量を変更する
                self.change_item_num()

                # 色情報取得
                # 色情報ヘッダーの取得　
                logout.output_log_debug(self, '色ヘッダーxpath: //body[@id="my"]/div[8]/div[2]/div/div/table/tbody/tr/th')
                color_header = self.DRIVER.find_elements_by_xpath(
                    '//body[@id="my"]/div[8]/div[2]/div/div/table/tbody/tr/th')

                # 色情報のリストを作成
                color_list = [v.text for i, v in enumerate(color_header) if i >= 2 and v is not None]
                logout.output_log_debug(self, '色ヘッダー取得内容:' + str(color_list))

                # サイズ情報の取得
                logout.output_log_debug(self, 'サイズカラムxpath: //*[@id="my"]/div[10]/div[2]/div/div[1]/table/tbody/tr')
                size_row = self.DRIVER.find_elements_by_xpath('//*[@id="my"]/div[8]/div[2]/div/div[1]/table/tbody/tr')

                # サイズ情報のリストを作成
                size_list = [w[0].text for i, w in enumerate([v.find_elements_by_tag_name('td') for v in size_row])
                             if i >= 1 and w is not None]
                logout.output_log_debug(self, 'サイズカラム取得内容: ' + str(size_list))
                # size_list = [x.find_elements_by_id('td')[0].text for x in size_list]

                # 変更箇所の確定
                # 引数に設定された商品の色とリスト内(color_list)の色が一致した箇所の保存
                # 色情報をリスト内からの検索
                color_place_dict = {}
                for color_index, color in enumerate(color_list):
                    for item_info in input_data.item_info:
                        if item_info.color == color:
                            # 色の列数が「tr[2]」から色の列になる
                            color_place_dict[color] = color_index + 3
                logout.output_log_debug(self, '入力用インデックス色情報：' + str(color_place_dict))

                # 引数に設定された商品のサイズとリスト内(size_list)のサイズが一致した箇所の保存
                size_place_map = {}
                for size_index, size in enumerate(size_list):
                    for item_info in input_data.item_info:
                        if item_info.size == size:
                            # サイズの行数が「td[3]」からサイズの行になる
                            size_place_map[size] = size_index + 2
                logout.output_log_debug(self, '入力用インデックス色情報 :' + str(size_place_map))

                # 商品入力用のオブジェクト取得(Selenium上で商品の有無のリストボックスを操作できるよう取得)
                for item_info in input_data.item_info:
                    # 「手元に在庫あり」の商品は更新対象外
                    if item_info.existence != Existence.IN_STOCK_AT_HAND:
                        input_item_xpath = '//*[@id="my"]/div[8]/div[2]/div/div[1]/table/tbody/tr[' \
                                           + str(size_place_map[item_info.size]) + ']/td[' \
                                           + str(color_place_dict[item_info.color]) + ']/div/select'
                        item_inventory = self.DRIVER.find_element_by_xpath(input_item_xpath)
                        logout.output_log_debug(self, '入力用Xpath: ' + input_item_xpath)

                        # ここで商品の各リストボックスを扱う
                        item_inventory.click()
                        item_selected = Select(item_inventory)
                        if item_info.existence == Existence.IN_STOCK:
                            item_selected.select_by_index(0)
                        elif item_info.existence == Existence.IN_STOCK:
                            item_selected.select_by_index(1)
                    else:
                        logout.output_log_info(self, '更新対象外の商品情報: 商品ID:' + input_data.item_id + ' ' + str(item_info))

                # 商品情報確定ボタン
                update_button = self.DRIVER.find_element_by_xpath('//*[@id="my"]/div[8]/div[2]/div/div[3]/a[2]')
                update_button.click()
                break
        # テスト用
        # image_dir = '/Users/seita/Program/python/stock_info_transfer/test_image/after_input.png'
        # self.DRIVER.save_screenshot(image_dir)

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

    def click_next_button(self):
        """
        buyma上の表示件数が最大表示数を超えていた場合に画面を遷移させて商品を表示していく
        """
        # アクセスが失敗した場合にリトライを行う
        retry = 0
        error = None
        while retry < self.__RETRIES:
            try:
                # 次へボタン表示待機
                WebDriverWait(self.DRIVER, self.__TIMEOUT_VERY_SHOT).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@rel="next" and text() = "次へ"]'))
                )
                # 画面上に「次へ」ボタンの検索
                next_button = self.DRIVER.find_elements_by_xpath('//*[@rel="next" and text() = "次へ"]')

                # 「次へ」ボタンの存在確認
                if next_button:
                    next_button[0].click()

                time.sleep(self.__TIMEOUT_VERY_SHOT)

            except TimeoutException as te:
                retry += 1
                error = te
                self.first_page_access()
                continue

            else:
                break
        else:
            logout.output_log_error(self, log_message='商品一覧ページの「次へ」ボタン押下処理に失敗しました。', err=error)
            raise error

    def check_next_button(self) -> bool:
        """
        buyma上「次へ」ボタンの確認
        """
        # 画面上に「次へ」ボタンの検索
        next_button = self.DRIVER.find_elements_by_xpath('//*[@rel="next" and text() = "次へ"]')

        # 「次へ」ボタンの存在確認
        if next_button:
            check_button = True
        else:
            check_button = False

        return check_button

    def first_page_access(self):
        """
        商品リストの最初のページへアクセスする
        """
        self.DRIVER.get('https://www.buyma.com/my/sell/?page=1&tab=b#/')

    def change_display_matter(self):
        """
        表示件数を表示数最大の100へ変更する
        """
        # アクセスが失敗した場合にリトライを行う
        retry = 0
        error = None
        while retry < self.__RETRIES:
            try:
                # 表示件数表示待機
                WebDriverWait(self.DRIVER, self.__TIMEOUT_VERY_SHOT).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="row-count-options"]'))
                )
                self.DRIVER.find_element_by_xpath('//*[@id="row-count-options"]').click()

                # 表示件数表示ドロップダウンクリック待機
                WebDriverWait(self.DRIVER, self.__TIMEOUT_VERY_SHOT).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="row-count-options"]/option[3]'))
                )
                self.DRIVER.find_element_by_xpath('//*[@id="row-count-options"]/option[3]').click()

            except TimeoutException as te:
                retry += 1
                error = te
                self.first_page_access()
                continue

            else:
                break
        else:
            logout.output_log_error(self, log_message='表示件数変更処理に失敗しました。', err=error)
            raise error

    def change_item_num(self):
        """
        入力した商品に対して数量をデフォルトで設定する
        """
        # アクセスが失敗した場合にリトライを行う
        retry = 0
        error = None
        while retry < self.__RETRIES:
            try:
                # 表示件数表示待機
                WebDriverWait(self.DRIVER, self.__TIMEOUT_VERY_SHOT).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="my"]/div[8]/div[2]/div/div[2]'
                                                                '/div/div[1]/span/input[1]'))
                )

                item_num = self.DRIVER.find_elements_by_xpath('//*[@id="my"]/div[8]/div[2]/div/div[2]'
                                                              '/div/div[1]/span/input[1]')
                for num in item_num:
                    # 数量入力時に全ての商品が在庫なしになっている場合、テキストボックスが非活性になっているため入力をしない
                    if num.is_enabled():
                        num.clear()
                        num.send_keys('10')

            except TimeoutException as te:
                retry += 1
                error = te
                continue

            else:
                break
        else:
            logout.output_log_error(self, log_message='買付可能数変更処理に失敗しました。', err=error)
            raise error

    def wait_lord(self):
        """
        サイト上の要素が全て読み込めているかを返す
        Returns:
            bool: True サイトの読み込みが完了, False サイトの読み込みが未完
        """
        page_state = self.DRIVER.execute_script('return document.readyState;')
        return page_state == 'complete'

    def get_now_html(self):
        """
        現在のHTMLソースを返す
        Returns:
            Union[int, List[Union[int, str]]]: 現在ブラウザが参照しているHTML
        """
        return self.DRIVER.page_source
