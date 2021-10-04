from collections import defaultdict
import re
from typing import Dict, Tuple
import dill

import pandas as pd

from exception.exceptions import AppRuntimeException
from utils import csv
from scrape.buyma_scraper import BuymaScraper
from scrape.asos_scraper import AsosScraper
from scrape.end_scraper import EndScraper
from setting import settings


class InventoryManager():

    def __init__(self) -> None:
        self.buyma = BuymaScraper()
        self.buyma.login()

        self.asos = AsosScraper()
        self.asos.go_top_page()
        self.end = EndScraper()
        self.end.go_top_page()

        self.last_time_stock = self.load_last_time_stock(settings.last_stock_path)
    
    @staticmethod
    def load_last_time_stock(path: str) -> Dict[str, Dict[str, Dict[str, bool]]]:
        try:
            with open(path, 'rb') as f:
                last_time_stock = dill.load(f)
        except EOFError:
            last_time_stock = dict()

        return last_time_stock

    @staticmethod
    def save_last_time_stock(path, last_time_stock: Dict[str, Dict[str, Dict[str, bool]]]) -> None:
        with open(path, 'wb') as f:
            dill.dump(last_time_stock, f)

    @staticmethod
    def apply_save_keys(input_df: pd.DataFrame, save_keys: pd.DataFrame) -> pd.DataFrame:
        """ セーブキーを反映して今回処理対象のキーを作成する

        Args:
            input_df (pd.DataFrame): inputデータ（全データ）
            save_keys (pd.DataFrame): セーブキー

        Returns:
            pd.DataFrame:　今回処理対象のキー
        """
        
        # 在庫反映の単位となるキー項目を取得
        keys = input_df[['id_buyma']]
        # 重複を削除する。
        keys = keys[~keys.duplicated()]
        # セーブデータがある場合は、途中から処理を行うため、キー項目から削除
        keys = keys[~keys.isin(save_keys.to_dict(orient='list')).all(1)]

        return keys

    def load_input_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """ 処理に必要なデータをロードする

        Returns:
            tuple: 補正後のinputデータ, セーブデータ
        """

        # inputデータの読み込み
        input_df = csv.read_csv(settings.input_csv_path)
        
        # inputデータのURLの不要なパスパラメータを削除し補正する。
        input_df['url_supplier'] = input_df['url_supplier'].apply(lambda url: re.sub('\?.*', '', url))
        input_df['error'] = ''
        # 補正後のinputデータを保存　
        # TODO この処理は消していいかも（補正処理は毎回行うため）
        csv.save_csv(settings.input_csv_path, input_df)

        # セーブデータの読み込み
        try:
            save_df = csv.read_csv(settings.save_csv_path)
        except FileNotFoundError:
            # ファイルが存在しない場合はセーブデータ無しと判断する
            save_df = pd.DataFrame(index=[], columns=['id_buyma'])
        
        return input_df, save_df

    def get_stock_from_supplier(self, id_buyma: str, input_df: pd.DataFrame) -> Tuple[defaultdict[str, defaultdict[str, bool]], bool]:
        """ 買い付け先から在庫取得する

        Args:
            url (str): 買い付け先の商品URL
            size_data (pd.DataFrame): サイズデータ（'size_supplier', 'size_buyma'列）

        Returns:
            Tuple[defaultdict[str, defaultdict[str, bool]], bool]: 
                ({'color表記' : {'Buymaのサイズ表記': '在庫の有無(True(有り)/False(無し))'}, 設定誤りのサイズリスト)
        """
        all_stock_data = defaultdict(lambda: defaultdict(bool))
        mistake_flg = False
        
        # キーが一致するデータ（複数）を取得する
        target_id_df = input_df[(input_df['id_buyma'] == id_buyma)]
        duplicate_df = target_id_df[~target_id_df[['url_supplier']].duplicated()]
        keys = duplicate_df[['url_supplier', 'color_info_buyma']]
        for _, row in keys.iterrows():
            url_supplier, color_info_buyma = row[0], row[1]
        

            target_data = input_df[
                (input_df['id_buyma'] == id_buyma)
                & (input_df['url_supplier'] == url_supplier)
                & (input_df['color_info_buyma'] == color_info_buyma)]
                    
            size_data = target_data[['size_supplier', 'size_buyma']]

            # {'仕入れ先のsize表記': 'buymaのsize表記'}のdictを作成する
            size_data = {row[0]: row[1] for _, row in size_data.iterrows()}

            if 'https://www.asos.com' in url_supplier:
                supplier = self.asos
            elif 'https://www.endclothing.com/' in url_supplier:
                supplier = self.end

            stock_data, mistake_list = supplier.run(url_supplier, size_data)
            
            for size, is_stock in stock_data.items():
                all_stock_data[color_info_buyma][size] = all_stock_data[color_info_buyma][size] or is_stock

        
            if mistake_list:
                # supplierのサイズ設定ミスをinputに出力
                input_df.loc[
                    (input_df['id_buyma'] == id_buyma)
                    & (input_df['url_supplier'] == url_supplier)
                    & (input_df['color_info_buyma'] == color_info_buyma)
                    & (input_df['size_supplier'].isin(mistake_list))
                    , 'error'
                    ] = 'size_supplier mistake'
                mistake_flg = True

        return all_stock_data, mistake_flg

    
    def change_stock_to_seller(self, buyma_id: str, stock_data: defaultdict[str, defaultdict[str, bool]], input_df: pd.DataFrame) -> bool:
        """ 在庫を反映する

        Args:
            buyma_id (str): 在庫を反映するbuymaの商品ID
            color (str): 在庫を反映するbuymaの商品カラー
            stock_data (Dict[str, bool]): 仕入れ先から取得した在庫情報
        """
        if not stock_data:
            return
        
        mistake_dict = self.buyma.run(buyma_id, stock_data)

        mistake_flg = False
        if mistake_dict:
            for color, mistake_list in mistake_dict.items():
                input_df.loc[
                    (input_df['id_buyma'] == buyma_id)
                    & (input_df['color_info_buyma'] == color)
                    & (input_df['size_buyma'].isin(mistake_list))
                    , 'error'
                    ] = 'size_buyma mistake'
            
            mistake_flg = True

        return mistake_flg

    def save_stock_data(self, id_buyma: str, stock_data: Dict[str, bool]) -> None:
        """ 在庫情報を保存する

        Args:
            id_buyma (str): [description]
            stock_data (Dict[str, bool]): [description]
        """
        self.last_time_stock[id_buyma] = stock_data

    def is_change_last_time(self, id_buyma: str, stock_data: Dict[str, bool]) -> bool:
        """ 前回の在庫情報から変更がある場合にTrueを返す

        Args:
            id_buyma (str): [description]
            stock_data (Dict[str, bool]): [description]

        Returns:
            bool: [description]
        """
        last_stock = self.last_time_stock.get(id_buyma, dict())
        
        return last_stock != stock_data

    def run(self):
        """ エントリポイント
        """
        # 処理に必要なデータをロードする
        input_df, save_keys = self.load_input_data()
        # セーブキーを反映し今回処理対象のキーを生成する
        keys = self.apply_save_keys(input_df, save_keys)
        try:
            for _, row in keys.iterrows():
                id_buyma = row[0]

                is_save_skip = False
                
                try:
                    # 買い付け先の在庫を取得
                    stock_data, is_mistake_supplier = self.get_stock_from_supplier(id_buyma, input_df)
                    if is_mistake_supplier:
                        is_save_skip = True

                    # buymaへ在庫反映を行う
                    if (self.is_change_last_time(id_buyma, stock_data)):
                        is_mistake_buyma = self.change_stock_to_seller(id_buyma, stock_data, input_df)

                        self.save_stock_data(id_buyma, stock_data)

                        if is_mistake_buyma:
                            is_save_skip = True

                except AppRuntimeException as e:
                    input_df.loc[
                        (input_df['id_buyma'] == id_buyma)
                        , 'error'
                        ] = e.message
                    is_save_skip = True

                # 正常に処理したキーをセーブキーに追加する。（設定ミスがある場合は追加しない。）
                if not is_save_skip:
                    save_keys = save_keys.append({'id_buyma': id_buyma}, ignore_index=True)
        
        finally:
            if not input_df[~(input_df['error'] == '')].empty:
                print('\n設定ミスがあります。\ninput.csvを確認してください。')
            if keys[~keys.isin(save_keys.to_dict(orient='list')).all(1)].empty:
                # 全て処理のキーを処理した場合はセーブデータを削除する。
                csv.delete_csv(settings.save_csv_path)
            else:
                # 次回途中から処理開始できるよう、セーブキーを保存する
                csv.save_csv(settings.save_csv_path, save_keys)
            csv.save_csv(settings.input_csv_path, input_df)
            self.save_last_time_stock(settings.last_stock_path, self.last_time_stock)