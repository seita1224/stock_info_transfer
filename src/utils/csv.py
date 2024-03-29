import os

import pandas as pd


def read_csv(file_path: str) -> pd.DataFrame:
    """ csvファイルを読み込みdfを返却する

    Args:
        file_path (str): 読み込むファイルパス

    Returns:
        pd.DataFrame: 読み込んだデータ
    """

    df = pd.read_csv(file_path, encoding='utf-8')
    df = df.fillna('')

    return df

def save_csv(file_path: str, save_data: pd.DataFrame) -> None:
    """ dfをcsvに保存する処理

    Args:
        file_path (str): 保存するファイルパス
        save_data (pd.DataFrame): 保存データ
    """
    save_data.to_csv(file_path, encoding='utf-8', index=False)

def delete_csv(file_path) -> None:
    """ csvを削除する処理

    Args:
        file_path (str): 削除するファイルパス
    """
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass
