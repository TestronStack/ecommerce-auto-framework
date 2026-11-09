import time

import allure
import pytest

from api.product_api import ProductApi


@allure.feature("商品模块")
class TestProduct:

    @allure.story("新增商品")
    @allure.title("新增商品成功")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_product(self, product_api, temp_product):
        body = product_api.get_all_products().json()
        assert body["code"] == 200

        # 从列表里找到刚创建的商品，确认真的落库了
        ids = [p["id"] for p in body["data"]]
        assert temp_product["id"] in ids

    @allure.story("查询商品")
    @allure.title("查询所有商品")
    def test_get_all_products(self, product_api):
        body = product_api.get_all_products().json()

        assert body["code"] == 200
        assert isinstance(body["data"], list)

    @allure.story("查询商品")
    @allure.title("分页查询商品")
    def test_page_products(self, product_api):
        body = product_api.page_products(page=0, size=10).json()

        with allure.step("断言分页字段"):
            assert body["code"] == 200
            assert body["data"]["number"] == 0
            assert body["data"]["size"] == 10

    @allure.story("查询商品")
    @allure.title("按 ID 查询商品")
    def test_get_product_by_id(self, product_api, temp_product):
        body = product_api.get_product_by_id(temp_product["id"]).json()

        assert body["code"] == 200
        assert body["data"]["name"] == temp_product["name"]

    @allure.story("查询商品")
    @allure.title("查询不存在的商品，返回 404")
    def test_get_product_not_exist(self, product_api):
        body = product_api.get_product_by_id(999999).json()

        assert body["code"] == 404
        assert body["msg"] == "商品不存在"

    @allure.story("查询商品")
    @allure.title("按分类查询商品")
    def test_get_products_by_category(self, product_api, temp_product):
        body = product_api.get_products_by_category(temp_product["category_id"]).json()

        assert body["code"] == 200
        assert isinstance(body["data"], list)

    @allure.story("查询商品")
    @allure.title("按状态查询上架商品")
    def test_get_products_by_status(self, product_api):
        body = product_api.get_products_by_status(1).json()

        assert body["code"] == 200
        # 上架状态的商品 status 都应该是 1
        for product in body["data"]:
            assert product["status"] == 1

    @allure.story("查询商品")
    @allure.title("按名称搜索商品")
    def test_search_products(self, product_api, temp_product):
        # 用临时商品的完整名称搜索，能搜到自己创建的那条
        body = product_api.search_products(temp_product["name"]).json()

        assert body["code"] == 200
        names = [p["name"] for p in body["data"]]
        assert temp_product["name"] in names

    @allure.story("查询商品")
    @allure.title("按价格区间查询商品")
    def test_get_products_by_price_range(self, product_api):
        body = product_api.get_products_by_price_range(0, 99999).json()

        assert body["code"] == 200
        for product in body["data"]:
            assert 0 <= product["price"] <= 99999

    @allure.story("更新商品")
    @allure.title("更新商品价格和库存")
    def test_update_product(self, product_api, temp_product):
        # 商品更新要传齐必填字段：name、price、stock
        payload = {
            "name": temp_product["name"],
            "price": 88.8,
            "stock": 66,
            "status": 1,
            "category": {"id": temp_product["category_id"]},
        }
        body = product_api.update_product(temp_product["id"], payload).json()

        with allure.step("断言价格和库存已更新"):
            assert body["code"] == 200
            assert body["data"]["price"] == 88.8
            assert body["data"]["stock"] == 66

    @allure.story("权限控制")
    @allure.title("权限用例：{role} 账号删除商品，预期返回 {expect_code}")
    @pytest.mark.parametrize("role_token, expect_code", [("admin", 200), ("user", 403)],
                             indirect=["role_token"])
    def test_delete_product_permission(self, role_token, expect_code, admin_token, default_category_id):
        # 每个参数单独创建一个商品
        name = "delgoods_" + str(expect_code) + "_" + str(int(time.time()))
        created = ProductApi(admin_token).create_product(
            name, 10.0, 5, category_id=default_category_id
        ).json()
        assert created["code"] == 200
        product_id = created["data"]["id"]

        body = ProductApi(role_token).delete_product(product_id).json()

        with allure.step("断言删除结果符合角色权限"):
            assert body["code"] == expect_code

        if expect_code == 200:
            assert ProductApi(admin_token).get_product_by_id(product_id).json()["code"] == 404
        else:
            # 403 时商品还在，用管理员清理
            ProductApi(admin_token).delete_product(product_id)
