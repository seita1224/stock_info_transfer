from enum import Enum


class Existence(Enum):
    """
    商品在庫状態
    """
    # 未入力または存在しない値の入力
    NO_INPUT = 0

    # 在庫あり
    IN_STOCK = 1

    # 在庫なし
    OUT_OF_STOCK = 2

    # 手元に在庫あり
    IN_STOCK_AT_HAND = 3

