class UserConst:
    DEFAULT_REAL_NAME = "vip用户%s"
    DEFAULT_REAL_AVATAR = "https://static-inc.xiwang.com/nayncat/__private__/64e6cc024b09442f49ab9b98" \
                          "/Vc9mbpbg1f9FbnEW3GzqY"

    REFRESH_TOKEN_EXPIRE = 24 * 60 * 60

    # 实际路由为 API_PREFIX(/pulse) + /user/refresh, 此处必须与完整路径一致, 否则浏览器不会下发该 Cookie
    COOKIE_API_PATH = "/pulse/user/refresh"
