"""
このシステムのログの形を定型化するためのモジュール全オブジェクトにてこのモジュールを使用しログの出力を行う
Todo:
    例外処理時のメッセージをより簡単に表示できるようにする
"""
import logging
from logging import getLogger
import os


logger = getLogger('stock_info_transfer')
# handler = logging.FileHandler('./log/stock_info_transfer.log')

file_handler_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'log', 'stock_info_transfer.log')
handler = logging.FileHandler(file_handler_path)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))
logger.addHandler(handler)


def output_log_info(class_obj=None, log_message='EmptyMessage'):
    logger.setLevel(logging.INFO)
    logger.info(class_obj.__class__.__name__+ ':' + log_message)


def output_log_debug(class_obj=None, log_message='EmptyMessage'):
    logger.setLevel(logging.DEBUG)
    logger.debug(class_obj.__class__.__name__+ ':' + log_message)


def output_log_warning(class_obj=None, log_message='EmptyMessage'):
    logger.setLevel(logging.WARNING)
    logger.warning(class_obj.__class__.__name__+ ':' + log_message)


def output_log_error(class_obj=None, log_message='EmptyMessage'):
    logger.setLevel(logging.ERROR)
    logger.error(class_obj.__class__.__name__+ ':' + log_message)
