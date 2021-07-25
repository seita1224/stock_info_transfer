from typing import List

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from exception.exceptions import AppException
from setting import settings


ACCESS_RETRY_LIMIT = 3

class ElementNotFoundException(AppException):
    pass


class BaseScraper:
    driver = None
    web_wait = None
    
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
        self.driver.implicitly_wait(5)

        self.web_wait = WebDriverWait(self.driver, 10)

    def __close_driver(self) -> None:
        """　Chromeドライバーの削除処理
        """
        self.driver.close()
        self.driver.quit()
    
    def get_element_by_xpath_short_wait(self, xpath: str) -> WebElement:
        try:
            element = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.XPATH, xpath)))

        except TimeoutException:
            # TODO 適切なメッセージの検討
            raise ElementNotFoundException(f'xpath: {xpath}')

        return element
    
    def get_element_by_xpath(self, xpath: str) -> WebElement:
        """ 単一のelementを取得する（xpath指定）
        Args:
            xpath (str): 取得するElementのxpath

        Raises:
            ElementNotFoundException: 現在のページでElementが見つからなかった場合に発生

        Returns:
            WebElement: 取得したElement
        """
        try:
            element = self.web_wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))

        except TimeoutException:
            # TODO 適切なメッセージの検討
            raise ElementNotFoundException(f'xpath: {xpath}')

        return element
    
    def get_elements_by_xpath(self, xpath: str) -> List[WebElement]:
        """ 複数のelementをListで取得する（xpath指定）

        Args:
            xpath (str): 取得するElementのxpath

        Raises:
            ElementNotFoundException: 現在のページでElementが見つからなかった場合に発生

        Returns:
            WebElement: 取得したElement
        """
        try:
            elements = self.web_wait.until(EC.visibility_of_all_elements_located((By.XPATH, xpath)))
        except TimeoutException:
            # TODO 適切なメッセージの検討
            raise ElementNotFoundException(f'xpath: {xpath}')

        return elements
    
def scrape_retry(func):
    """　サイトアクセスを再試行するデコレーターメソッド
    　　　Exceptionが発生した場合、再施行する（`ACCESS_RETRY_LIMIT`まで）
    Args:
        func: 
    """
    def wrapper(*args, **kwargs):
        for _ in range(ACCESS_RETRY_LIMIT):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error = e
        else:
            raise error
    
    return wrapper
