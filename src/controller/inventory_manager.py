import re
from typing import Dict, List, Tuple

import pandas as pd

from exception.exceptions import AppRuntimeException
from utils import csv
from scrape.buyma_scraper import BuymaScraper
from scrape.asos_scraper import AsosScraper
from setting import settings


class InventoryManager():

    def __init__(self) -> None:
        self.asos = AsosScraper()
        self.buyma = BuymaScraper()
        self.buyma.login()

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
        keys = input_df[['id_buyma', 'url_supplier', 'color_info_buyma']]
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
            save_df = pd.DataFrame(index=[], columns=['id_buyma', 'url_supplier', 'color_info_buyma'])
        
        return input_df, save_df

    def get_stock_from_supplier(self, url: str, size_data_df: pd.DataFrame) -> Tuple[Dict[str, bool], List[str]]:
        """ 買い付け先から在庫取得する

        Args:
            url (str): 買い付け先の商品URL
            size_data (pd.DataFrame): サイズデータ（'size_supplier', 'size_buyma'列）

        Returns:
            Tuple[Dict[str, bool], List[str]]: 
                ({'Buymaのサイズ表記': '在庫の有無(True(有り)/False(無し))'}, 設定誤りのサイズリスト)
        """
        # {'仕入れ先のsize表記': 'buymaのsize表記'}のdictを作成する
        size_data = {row[0]: row[1] for _, row in size_data_df.iterrows()}

        return self.asos.run(url, size_data)

    
    def change_stock_to_seller(self, buyma_id: str, color: str, stock_data: Dict[str, bool]) -> None:
        """ 在庫を反映する

        Args:
            buyma_id (str): 在庫を反映するbuymaの商品ID
            color (str): 在庫を反映するbuymaの商品カラー
            stock_data (Dict[str, bool]): ASOSから取得した在庫情報
        """

        self.buyma.run(buyma_id, color, stock_data)

    def run(self):
        """ エントリポイント
        """
        # 処理に必要なデータをロードする
        input_df, save_keys = self.load_input_data()
        # セーブキーを反映し今回処理対象のキーを生成する
        keys = self.apply_save_keys(input_df, save_keys)
        try:
            for _, row in keys.iterrows():
                id_buyma, url_supplier, color_info_buyma = row[0], row[1], row[2]
                
                # キーが一致するデータ（複数）を取得する
                target_data = input_df[
                    (input_df['id_buyma'] == id_buyma)
                     & (input_df['url_supplier'] == url_supplier)
                     & (input_df['color_info_buyma'] == color_info_buyma)]
                
                size_data = target_data[['size_supplier', 'size_buyma']]
                try:
                    # 買い付け先の在庫を取得
                    stock_data, mistake_size_list = self.get_stock_from_supplier(url_supplier, size_data)
                    if mistake_size_list:
                        # Asosのサイズ設定ミスをinput.csvに出力
                        input_df.loc[
                            (input_df['id_buyma'] == id_buyma)
                            & (input_df['url_supplier'] == url_supplier)
                            & (input_df['color_info_buyma'] == color_info_buyma)
                            & (input_df['size_supplier'].isin(mistake_size_list))
                            , 'error'
                            ] = 'size_supplier mistake'

                    # buymaへ在庫反映を行う
                    self.change_stock_to_seller(id_buyma, color_info_buyma, stock_data)
                except AppRuntimeException as e:
                    # TODO 
                    # input_dataに問題内容を列として追加。最後にコンソールにinputdataをみるよう出力する。
                    input_df.loc[
                        (input_df['id_buyma'] == id_buyma)
                        & (input_df['url_supplier'] == url_supplier)
                        & (input_df['color_info_buyma'] == color_info_buyma)
                        , 'error'
                        ] = e.message
                    continue

                # 処理したキーをセーブキーに追加する
                # TODO 都度新しいオブジェクトを作っているため、負荷がかかりそう。
                save_keys = save_keys.append({'id_buyma': row[0], 'url_supplier': row[1]}, ignore_index=True)
                
            # TODO この判定がうまく機能していない
            if keys[~keys.isin(save_keys.to_dict(orient='list')).all(1)].empty:
                # 全て処理のキーを処理した場合はセーブデータを空にする。
                save_keys = pd.DataFrame(index=[], columns=['id_buyma', 'url_supplier'])
        
        finally:
            # 次回途中から処理開始できるよう、セーブキーを保存する
            csv.save_csv(settings.save_csv_path, save_keys)
            csv.save_csv(settings.input_csv_path, input_df)