import re
from typing import Tuple

import pandas as pd

from utils import csv
from scrape.buyma_scraper import BuymaScraper
from scrape.asos_scraper import AsosScraper
from setting import settings

class InventoryManager():

    def __init__(self) -> None:
        # self.asos = AsosScraper()
        # self.buyma = BuymaScraper()
        self.asos = None
        self.buyma = None
    
    @staticmethod
    def modify_supplier_url(df: pd.DataFrame) -> pd.DataFrame:
        """ inputデータのURLの不要なパスパラメータを削除し補正する。
        Args:
            df (pd.DataFrame): inputデータ

        Returns:
            pd.DataFrame: 補正後のinputデータ
        """
        df['url_supplier'] = df['url_supplier'].apply(lambda url: re.sub('\?.*', '', url))

        return df

    def preprocess(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """ メイン処理に必要な前処理を実施

        Returns:
            tuple: 補正後のinputデータ, セーブデータ
        """

        # inputデータの読み込み
        input_df = csv.read_csv(settings.input_csv_path)
        # inputデータの補正処理
        input_df = self.modify_supplier_url(input_df)
        # 補正後のinputデータを保存　
        # TODO この処理は消していいかも（補正処理は毎回行うため）
        csv.save_csv(settings.input_csv_path, input_df)

        # セーブデータの読み込み
        try:
            save_df = csv.read_csv(settings.save_csv_path)
        except FileNotFoundError:
            # ファイルが存在しない場合はセーブデータ無しと判断する
            save_df = pd.DataFrame(index=[], columns=['id_buyma', 'url_supplier'])
        
        return input_df, save_df

        # item_info = input_df[['id_buyma', 'url_supplier']]
        # csv.save_csv(settings.save_csv_path, item_info[~item_info.duplicated()])

    def get_stock_from_supplier(self, dict) -> dict:
        self.asos.get_stock(None)
    
    def change_stock_to_seller(self, dict):
        self.buyma.change_stock(None)

    def run(self):
        """ エントリポイント
        """
        input_df, save_keys = self.preprocess()
        # 在庫反映の単位となるキー項目を取得
        keys = input_df[['id_buyma', 'url_supplier']]
        # 重複を削除する。
        keys = keys[~keys.duplicated()]
        # セーブデータがある場合は、途中から処理を行うため、キー項目から削除
        keys = keys[~keys.isin(save_keys.to_dict(orient='list')).all(1)]

        try:
            for _, row in keys.iterrows():
                print(f'{row[0]}, {row[1]}')
                target_data = input_df[(input_df['id_buyma'] == row[0]) & (input_df['url_supplier'] == row[1])]

                # データの加工処理（ASOSインプット用）

                # self.change_stock_to_seller(None)

                # データの加工処理（BUYMAインプット用）
                # self.get_stock_from_supplier(None)
                
                # 処理したキーをセーブキーに追加する
                save_keys = save_keys.append({'id_buyma': row[0], 'url_supplier': row[1]}, ignore_index=True)

            if keys[~keys.isin(save_keys.to_dict(orient='list')).all(1)].empty:
                # 全て処理のキーを処理した場合はセーブデータを空にする。
                save_keys = pd.DataFrame(index=[], columns=['id_buyma', 'url_supplier'])
        
        finally:
            # 次回途中から処理開始できるよう、セーブキーを保存する
            csv.save_csv(settings.save_csv_path, save_keys)

        
