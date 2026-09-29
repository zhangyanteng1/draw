class StringUtils:

    @staticmethod
    def str_not_none(s: str) -> bool:
        """ 判断字符串非 None """
        if s:
            return True
        return False

    @staticmethod
    def is_none(s: str) -> bool:
        return not StringUtils.str_not_none(s)

    @staticmethod
    def str_not_empty(s: str) -> bool:
        """ 判断字符串非 空字符串 """
        if s.strip() == "":
            return False
        return True

    @staticmethod
    def is_empty(s: str) -> bool:
        return not StringUtils.str_not_empty(s)
