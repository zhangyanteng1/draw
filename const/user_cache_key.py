class UserCacheKey:
    REFRESH_TOKEN = "refresh_token:%s"

    REFRESH_TOKEN_EXPIRE = 24 * 60 * 60

    USER_LOGIN_ERROR = "login_error:%s"

    USER_LOGIN_BLACK = "login_ip_black:%s"

    USER_LOGIN_ERROR_EXPIRE = 5 * 60

    TOKEN_BLACKLIST = "token_blacklist:%s"

