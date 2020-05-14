import logout


class CsvParse:
    """
    商品情報を更新したいcsvが記載されているcsvを以下の形のdict形式に変換する
    取得するcsvの形式: 商品ID(buyma),商品URL(仕入先),サイズ(buyma),サイズ(仕入先),色情報(buyma)
    dict<str:dict<str:dict<str:str>>>: csvの解析結果<商品ID(buyma):<色情報(buyma):<サイズ(buyma):<サイズ(仕入先):商品URL(仕入先)>>>>
    """

    def __init__(self, file_path):
        self.__file_path = file_path
        self.__csv_text_lines = []
        self.get_csv_text()

    def get_csv_text(self):
        """
        Returns:
            str: 解析を行うCSVのテキスト情報
        """
        try:
            with open(self.__file_path, mode='r') as f:
                self.__csv_text_lines = f.readlines()
        except IOError as e:
            logout.output_log_error(self, '指定されたパスにCSVファイルが存在しません')

    def create_csv_text_for_dict(self):
        """
        CSVテキストの内容をデータを辞書型に変更して返す
        Returns:
          dict<str:dict<str:dict<str:str>>>: csvの解析結果<商品ID(buyma):<色情報(buyma):<サイズ(buyma):<サイズ(仕入先):商品URL(仕入先)>>>>
        """
        item_dict = dict()    # 商品ID

        for csv_row in self.__csv_text_lines:
            item_info = csv_row.split(',')
            item_info = list(map(self.clear_text, item_info))
            item_dict[item_info[0]] = {item_info[1]: {item_info[2]: {item_info[3]: {item_info[4]}}}}

        return item_dict

    def clear_text(self, clear_text: str):
        return clear_text.strip('\n')
