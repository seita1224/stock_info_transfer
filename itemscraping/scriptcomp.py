from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
import chromedriver_binary

class ScriptCompyle():
    """
    urlのサイトからjavascriptのデータを動かした状態のhtmlを返す
    """
    # サイトのURL
    SITE_URL = None

    def __init__(self, url):
        """
        Args:
            url(str):在庫取得先のURL
        """
        if isinstance(url,str):
            self.SITE_URL = url
        else:
            raise ValueError('urlには文字列の指定を行ってください')

    def script_compaill(self):
        """
        javascriptコンパイル済みのhtmlを返します。
        Return:
            driver.page_source(str):javascriptコンパイル済みhtml
        """
        # ブラウザのオプションを格納する変数をもらってきます。
        options = ChromeOptions()

        # ヘッドレスモードを有効にする（次の行をコメントアウトすると画面が表示される）。
        options.add_argument('--headless')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36')

        # ChromeのWebDriverオブジェクトを作成する。
        driver = Chrome(options=options)

        # Googleのトップ画面を開く。
        driver.get(self.SITE_URL)

        #javascriptをコンパイルしたhtmlを返す
        return driver.page_source

