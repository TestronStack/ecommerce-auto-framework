import time

import allure
import pytest

from api.category_api import CategoryApi


@allure.feature("分类模块")
class TestCategory:

    @allure.story("新增分类")
    @allure.title("新增分类成功")
    def test_create_category(self, category_api, temp_category):
        body = category_api.get_category_by_id(temp_category["id"]).json()

        assert body["code"] == 200
        assert body["data"]["name"] == temp_category["name"]

    @allure.story("查询分类")
    @allure.title("查询所有分类")
    def test_get_all_categories(self, category_api):
        body = category_api.get_all_categories().json()

        assert body["code"] == 200
        assert isinstance(body["data"], list)

    @allure.story("查询分类")
    @allure.title("查询不存在的分类，返回 404")
    def test_get_category_not_exist(self, category_api):
        body = category_api.get_category_by_id(999999).json()

        assert body["code"] == 404
        assert body["msg"] == "分类不存在"

    @allure.story("查询分类")
    @allure.title("查询顶级分类")
    def test_get_top_categories(self, category_api):
        body = category_api.get_top_categories().json()

        assert body["code"] == 200
        assert isinstance(body["data"], list)

    @allure.story("查询分类")
    @allure.title("查询子分类")
    def test_get_child_categories(self, category_api, default_category_id):
        body = category_api.get_child_categories(default_category_id).json()

        assert body["code"] == 200
        assert isinstance(body["data"], list)

    @allure.story("查询分类")
    @allure.title("查询启用的分类")
    def test_get_active_categories(self, category_api):
        body = category_api.get_active_categories().json()

        assert body["code"] == 200
        for category in body["data"]:
            assert category["status"] == 1

    @allure.story("更新分类")
    @allure.title("更新分类名称和描述")
    def test_update_category(self, category_api, temp_category):
        payload = {
            "name": temp_category["name"],
            "description": "更新后的描述",
            "sort": 20,
            "status": 1,
        }
        body = category_api.update_category(temp_category["id"], payload).json()

        with allure.step("断言描述已更新"):
            assert body["code"] == 200
            assert body["data"]["description"] == "更新后的描述"

    @allure.story("权限控制")
    @allure.title("权限用例：{role} 账号删除分类，预期返回 {expect_code}")
    @pytest.mark.parametrize("role_token, expect_code", [("admin", 200), ("user", 403)],
                             indirect=["role_token"])
    def test_delete_category_permission(self, role_token, expect_code, admin_token):
        # 每个参数单独创建一个分类
        name = "delcate_" + str(expect_code) + "_" + str(int(time.time()))
        created = CategoryApi(admin_token).create_category(name).json()
        assert created["code"] == 200
        category_id = created["data"]["id"]

        body = CategoryApi(role_token).delete_category(category_id).json()

        with allure.step("断言删除结果符合角色权限"):
            assert body["code"] == expect_code

        if expect_code == 200:
            assert CategoryApi(admin_token).get_category_by_id(category_id).json()["code"] == 404
        else:
            CategoryApi(admin_token).delete_category(category_id)
