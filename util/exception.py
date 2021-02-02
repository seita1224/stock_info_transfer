class ItemIdException(Exception):
    """
    商品IDに関連するエラーの場合使用する
    """
    pass


class HtmlException(Exception):
    """
    ページソースが生成(または取得)できなかった場合などHTMLソースに異常があった場合に使用する
    """
    pass
