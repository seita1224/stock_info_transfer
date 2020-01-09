"""
サイトのメタ情報あらかじめ設定ファイルから読み込み
上位クラスから入力されたサイト名を元にURL、ユーザ情報およびサイトのメタ情報を返す
"""


class SitesMeta:
    def __init__(self, site_name):
        """
        引数のサイト名からサイトの情報を読み込みデータの取得の準備を行う
        Args:
            site_name (str):サイト名
        Todo:
            サイト名から取得対象データを全て読み込み保存する処理を書き込む
        """
        pass

    def site_meta(self, data_name):
        """
        サイトのどの情報を取得するか指定し、指定されたデータを返す
        Args:
            data_name (str):データの名前
        Returns:
            object: 指定されたデータの中身
        Todo:
            指定されたデータ名(キー名)の中身を返す
        """
        pass

    def data_name_list(self):
        """
        Returns:
            list<str>: データの名前を全て返す
        Todo:
            データ名を全て返す(設定ファイル内のキー)
        """
        pass

