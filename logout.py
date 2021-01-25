"""
このシステムのログの形を定型化するためのモジュール全オブジェクトにてこのモジュールを使用しログの出力を行う
Todo:
    例外処理時のメッセージをより簡単に表示できるようにする
"""
import logging
from logging import getLogger, INFO
import os

file_name = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'log', 'stock_info_transfer.log')
logger = getLogger('stock_info_transfer')
handler = logging.FileHandler(filename=file_name)
handler.setLevel(INFO)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))
logger.setLevel(INFO)
logger.addHandler(handler)


def output_log_info(class_obj=None, log_message='EmptyMessage'):
    logger.info(class_obj.__class__.__name__ + ':' + log_message)


def output_log_debug(class_obj=None, log_message='EmptyMessage'):
    logger.debug(class_obj.__class__.__name__ + ':' + log_message)


def output_log_warning(class_obj=None, log_message='EmptyMessage'):
    logger.warning(class_obj.__class__.__name__ + ':' + log_message)


def output_log_error(class_obj=None, log_message='EmptyMessage', err=None):
    logger.error(class_obj.__class__.__name__ + ':' + log_message)
    if err is None: raise Exception('ログに正しい情報を設定してください。')
    logger.exception(err)
