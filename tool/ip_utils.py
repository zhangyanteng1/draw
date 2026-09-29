from fastapi import Request


class IpUtils:

    @staticmethod
    def get_client_ip(request: Request) -> str:
        """
        获取客户端真实 IP 地址
        优先从反向代理头部获取，依次尝试 X-Forwarded-For、X-Real-IP，最后回退到直连 IP
        """
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip.strip()

        if request.client:
            return request.client.host

        return ""
