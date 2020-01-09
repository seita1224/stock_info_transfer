"""
サイトにアクセスして操作を行う場合の処理を集めたモジュール
"""


import time

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
import chromedriver_binary


class SiteAccess():
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
        options.add_argument('--headless')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/79.0.3945.88 Safari/537.36')

        # ChromeのWebDriverオブジェクトを作成する。
        self.DRIVER = Chrome(options=options)

    def script_compile(self, site_name):
        """
        javascriptコンパイル済みのhtmlを返します。
        汎用的なメソッドとして残しておく
        Args:
            site_name (str):HTMLの取得を行うサイトのURL
        Returns:
            Union[int, list[Union[int,str]]]:javascriptがコンパイルされたHTML基本的には文字列が返される
        """
        # インスタンスにて指定したサイトにアクセスする(アクセスしたタイミングでjavascriptがコンパイルされる)
        self.DRIVER.get(url)

        # htmlを返す
        return self.DRIVER.page_source

    def login(self, site_name):
        """
        サイトログインを行い遷移したいURLに遷移する
        Args:
            site_name (str):ログインしたいサイト名
        """
        # ログイン先にアクセス
        self.DRIVER.get(login_url)

        # ID、PWの場所を指定して入力
        site_id = self.DRIVER.find_element_by_id('')
        site_id.send_keys(site_user_id)
        site_pw = self.DRIVER.find_element_by_id('')
        site_pw.send_keys(site_user_pw)

        # 入力待ち
        time.sleep(1)

        # ログインボタンを指定しクリック
        login_button = self.DRIVER.find_element_by_name('')
        login_button.click()

