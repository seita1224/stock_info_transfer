from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from exception.exceptions import AppRuntimeException
from setting import settings


ACCESS_RETRY_LIMIT = 3

class BaseScraper:
    driver = None
    
    def __init__(self) -> None:
        self.__open_driver()

    def __del__(self) -> None:
        self.__close_driver()
    
    def __open_driver(self) -> None:
        """ Chromeドライバーを生成する
        """
    
        options = ChromeOptions()

        if not settings.window_display:
            # ヘッドレスモードを有効にする（ウィンドウを非表示）
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        options.add_argument('--no-sandbox')
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument("--disable-application-cache")

        options.add_argument('--disable-desktop-notifications')
        options.add_argument('--disable-extensions')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36')
        options.add_argument('--lang=ja')
        options.add_argument('--blink-settings=imagesEnabled=false')
        self.driver = Chrome(executable_path=settings.chromedriver_path, options=options)
        self.driver.implicitly_wait(1)

    def __close_driver(self) -> None:
        """　Chromeドライバーの削除処理
        """
        self.driver.close()
        self.driver.quit()
    

    def scrape_deco(func):
        """　サイトアクセスを再試行するデコレーターメソッド
        　　　AppRuntimeExceptionが発生した場合、再施行する（`ACCESS_RETRY_LIMIT`まで）
        Args:
            func: 
        """
        def wrapper(*args, **kwargs):
            for _ in range(ACCESS_RETRY_LIMIT):
                try:
                    func(*args, **kwargs)
                except AppRuntimeException as e:
                    error = e
                else:
                    break
            else:
                raise error
        
        return wrapper