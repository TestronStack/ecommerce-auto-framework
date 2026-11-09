import time

import allure
import pytest

from api.user_api import UserApi
from tests.conftest import load_json


@allure.feature("用户模块")
class TestUser:

    @allure.story("查询用户")
    @allure.title("查询所有用户")
    def test_get_all_users(self, user_api):
        body = user_api.get_all_users().json()

        with allure.step("断言返回用户列表"):
            assert body["code"] == 200
            assert isinstance(body["data"], list)

    @allure.story("查询用户")
    @allure.title("分页查询用户")
    def test_page_users(self, user_api):
        body = user_api.page_users(page=0, size=5).json()

        with allure.step("断言分页结构"):
            assert body["code"] == 200
            assert body["data"]["number"] == 0
            assert body["data"]["size"] == 5
            assert len(body["data"]["content"]) <= 5

    @allure.story("查询用户")
    @allure.title("按 ID 查询用户")
    def test_get_user_by_id(self, user_api, temp_user):
        body = user_api.get_user_by_id(temp_user["id"]).json()

        assert body["code"] == 200
        assert body["data"]["username"] == temp_user["username"]

    @allure.story("查询用户")
    @allure.title("按用户名查询用户")
    def test_get_user_by_username(self, user_api, temp_user):
        body = user_api.get_user_by_username(temp_user["username"]).json()

        assert body["code"] == 200
        assert body["data"]["id"] == temp_user["id"]

    @allure.story("查询用户")
    @allure.title("查询不存在的用户，返回 404")
    def test_get_user_not_exist(self, user_api):
        body = user_api.get_user_by_id(999999).json()

        assert body["code"] == 404
        assert body["msg"] == "用户不存在"

    @allure.story("更新用户")
    @allure.title("局部更新用户：{item[case_name]}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("item", load_json("user_data.json")["update_user"],
                             ids=lambda item: item["case_name"])
    def test_update_user(self, user_api, temp_user, item):
        # 拷贝一份，避免修改 json 里的原始数据
        payload = dict(item["payload"])
        # 数据里指定了 user_id 就用它（测 404 场景），否则用临时用户
        user_id = item.get("user_id", temp_user["id"])

        body = user_api.update_user(user_id, payload).json()

        assert body["code"] == item["expect_code"]

    @allure.story("更新用户")
    @allure.title("只传 phone 时，用户名等其它字段保持不变")
    def test_update_user_keep_other_fields(self, user_api, temp_user):
        body = user_api.update_user(temp_user["id"], {"phone": "13700009999"}).json()

        with allure.step("断言手机号更新成功，用户名没有被改掉"):
            assert body["code"] == 200
            assert body["data"]["phone"] == "13700009999"
            assert body["data"]["username"] == temp_user["username"]

    @allure.story("权限控制")
    @allure.title("权限用例：{role} 账号删除用户，预期返回 {expect_code}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("role_token, expect_code", [("admin", 200), ("user", 403)],
                             indirect=["role_token"])
    def test_delete_user_permission(self, role_token, expect_code, admin_token):
        # 每个参数都新注册一个用户，两个参数互不影响
        username = "del_" + str(expect_code) + "_" + str(int(time.time()))
        register = UserApi().register(username, "123456", username + "@test.com").json()
        assert register["code"] == 200
        user_id = register["data"]["id"]

        body = UserApi(role_token).delete_user(user_id).json()

        with allure.step("断言删除结果符合角色权限"):
            assert body["code"] == expect_code

        if expect_code == 200:
            # 删除成功后再查，应该返回 404
            assert UserApi(role_token).get_user_by_id(user_id).json()["code"] == 404
        else:
            # 没权限时用户还在，用管理员清理
            admin_user_api = UserApi(admin_token)
            assert admin_user_api.get_user_by_id(user_id).json()["code"] == 200
            admin_user_api.delete_user(user_id)
