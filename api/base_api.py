import requests

from config.settings import API_URL


class BaseApi:
    """接口基类：统一管理请求地址、请求头和四种请求方法"""

    def __init__(self, token=None):
        self.base_url = API_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json;charset=UTF-8"})
        # 传了 token 就带上，所有接口复用同一个会话
        if token:
            self.session.headers.update({"Authorization": "Bearer " + token})

    def get(self, path, **kwargs):
        return self.session.get(self.base_url + path, **kwargs)

    def post(self, path, json=None, **kwargs):
        return self.session.post(self.base_url + path, json=json, **kwargs)

    def put(self, path, json=None, **kwargs):
        return self.session.put(self.base_url + path, json=json, **kwargs)

    def delete(self, path, **kwargs):
        return self.session.delete(self.base_url + path, **kwargs)
