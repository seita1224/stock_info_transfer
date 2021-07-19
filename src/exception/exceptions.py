
class AppException(Exception):
    """ 処理を継続しない例外の基底クラス
    """
    def __init__(self, message: str):
        self.message = message


class AppRuntimeException(Exception):
    """ 処理を継続する例外の基底クラス
    """
    def __init__(self, message: str):
        self.message = message
