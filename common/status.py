class Status:

    OK = 200
    ERROR = 500
    # 请求参数不合法(如字段缺失/类型错误), 客户端可预期错误
    PARAM_ERROR = 400
    TOKEN_EXPIRED = 401
    # 业务校验失败(状态/资格等可预期错误), 与 500 内部错误区分开
    BUSINESS_ERROR = 4000
    LOGIN_ENV_ERROR = 4001



