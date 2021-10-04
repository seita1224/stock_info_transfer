import configparser
import os


def get_abspath(relative_path: str) -> str:
    return os.path.abspath(relative_path)


def get_chromedriver_path() -> str:
    if os.name == 'posix':
        return get_abspath(conf['chrome']['chromedriver_path_mac'])
    else:
        return get_abspath(conf['chrome']['chromedriver_path_windows'])


def parse_str_to_bool(parse_word: str) -> bool:
    if parse_word.lower() == 'true':
        return True
    else:
        return False

conf = configparser.ConfigParser()
conf.read('../settings.ini')

input_csv_path = get_abspath(conf['input']['input_csv_path'])
save_csv_path = get_abspath(conf['input']['save_csv_path'])
last_stock_path = get_abspath(conf['input']['last_stock_path'])

chromedriver_path = get_chromedriver_path()
window_display = parse_str_to_bool(conf['chrome']['window_display'])

buyma_max_sales_count = conf['buyma']['max_sales_count']
extension_sales_week = conf['buyma']['extension_sales_week']