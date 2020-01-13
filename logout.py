"""
このシステムのログの形を定型化するためのモジュール全オブジェクトにてこのモジュールを使用しログの出力を行う
Todo:
    例外処理時のメッセージをより簡単に表示できるようにする
"""
import logging
from logging import getLogger

logger = getLogger('stock_info_transfer')
handler = logging.FileHandler('./log/stock_info_transfer.log')
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))
logger.addHandler(handler)


def output_log_info(class_name='EmptyClass', log_message='EmptyMessage'):
    logger.setLevel(logging.INFO)
    logger.info(class_name + ':' + log_message)


def output_log_debug(class_name='EmptyClass', log_message='EmptyMessage'):
    logger.setLevel(logging.DEBUG)
    logger.debug(class_name + ':' + log_message)


def output_log_warning(class_name='EmptyClass', log_message='EmptyMessage'):
    logger.setLevel(logging.WARNING)
    logger.warning(class_name + ':' + log_message)


def output_log_error(class_name='EmptyClass', log_message='EmptyMessage'):
    logger.setLevel(logging.ERROR)
    logger.error(class_name + ':' + log_message)
