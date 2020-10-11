"""
サイトのメタ情報あらかじめ設定ファイルから読み込み
上位クラスから入力されたサイト名を元にURL、ユーザ情報およびサイトのメタ情報を返す
"""
import os

import yaml
import logout
import traceback


class SitesMeta:
    # 設定ファイルのオブジェクト
    config_yaml = None

    # ショップの情報
    shop_info = None

    def __init__(self):
        """
        引数のサイト名からサイトの情報を読み込みデータの取得の準備を行う
        """
        # コンフィグファイルの読み込み
        config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'config', 'config.yaml')
        try:
            with open(config_path) as config_yaml_file:
                self.config_yaml = yaml.safe_load(config_yaml_file)

        except Exception as e:
            logout.output_log_error(class_obj=self, log_message=traceback.format_exc())
            raise IOError(e)

    def get_site_meta(self, data_names: str):
        """
        サイトのどの情報を取得するか指定し、指定されたデータを返す
        Args:
            data_names (str):データの名前(データの階層表現はサイト名から「.（ドット）」にて行う)
        Returns:
            Union(str,int,list,dict): 指定されたデータの中身
        """
        # 設定ファイルの情報を分ける
        data_name_list = data_names.split('.')

        # 辞書型の検索作業用
        data = None

        # 引数で受け取った階層まで読み込む
        try:
            data = self.config_yaml['Shop']
            for key in data_name_list:
                data = data[key]
        except Exception as e:
            logout.output_log_error(class_obj=self,log_message=traceback.format_exc())
            raise Exception('受け取ったキーの値が違います。')

        return data
