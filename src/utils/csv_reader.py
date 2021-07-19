import pandas as pd


def read_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(filepath=file_path, encoding='utf-8')

    return df
