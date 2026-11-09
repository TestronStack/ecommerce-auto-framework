import time

import allure

from api.user_api import UserApi
from config.settings import ADMIN_PASSWORD, ADMIN_USERNAME


@allure.feature("登录模块")
class TestLogin:
    """登录 + 注册接口"""

    @allure.story("管理员登录")
    @allure.title("使用正确的账号密码登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_admin_login_success(self):
        with allure.step("调用登录接口"):
            resp = UserApi().login(ADMIN_USERNAME, ADMIN_PASSWORD)
            body = resp.json()

        with allure.step("断言登录成功并返回 token"):
            assert body["code"] == 200
            assert body["msg"] == "登录成功"
            assert isinstance(body["data"]["token"], str)
            assert len(body["data"]["token"]) > 0
            assert body["data"]["user"]["role"] == "ADMIN"

    @allure.story("异常登录")
    @allure.title("密码错误登录失败，返回 401")
    def test_login_wrong_password(self):
        body = UserApi().login(ADMIN_USERNAME, "wrong_password").json()

        assert body["code"] == 401
        assert body["msg"] == "用户名或密码错误"

    @allure.story("异常登录")
    @allure.title("用户不存在登录失败，返回 401")
    def test_login_user_not_exist(self):
        body = UserApi().login("not_exist_user_999", "123456").json()

        assert body["code"] == 401

    @allure.story("注册")
    @allure.title("使用随机用户名注册新用户成功")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_success(self, user_api):
        # 用时间戳保证用户名和邮箱不重复
        username = "reg_" + str(int(time.time()))

        body = UserApi().register(username, "123456", username + "@test.com").json()

        with allure.step("断言注册成功，默认角色是 USER"):
            assert body["code"] == 200
            assert body["data"]["username"] == username
            assert body["data"]["role"] == "USER"
            # 密码是只写字段，响应里不应该出现
            assert "password" not in body["data"]

        # 清理：用管理员的接口对象删除这个用户
        user_api.delete_user(body["data"]["id"])

    @allure.story("注册")
    @allure.title("用户名重复注册失败，返回 400")
    def test_register_duplicate_username(self, user_api):
        username = "dup_" + str(int(time.time()))
        email = username + "@test.com"

        first = UserApi().register(username, "123456", email).json()
        assert first["code"] == 200

        second = UserApi().register(username, "123456", "other_" + email).json()

        with allure.step("断言重复用户名被拒绝"):
            assert second["code"] == 400
            assert "已存在" in second["msg"]

        user_api.delete_user(first["data"]["id"])

    @allure.story("注册")
    @allure.title("密码长度不足 6 位，注册失败返回 400")
    def test_register_short_password(self):
        username = "short_" + str(int(time.time()))

        body = UserApi().register(username, "123", username + "@test.com").json()

        assert body["code"] == 400

    @allure.story("鉴权")
    @allure.title("不带 token 访问用户列表，返回 401")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_without_token(self):
        body = UserApi().get_all_users().json()

        assert body["code"] == 401
