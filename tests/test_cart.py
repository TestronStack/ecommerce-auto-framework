import allure
import pytest


@allure.feature("购物车模块")
class TestCart:

    @pytest.fixture(autouse=True)
    def clean_cart(self, normal_cart_api, normal_user):
        """每个用例开始前先清空购物车，避免用例之间互相影响"""
        normal_cart_api.clear_cart(normal_user["id"])
        yield

    @allure.story("加入购物车")
    @allure.title("加入购物车成功")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart(self, normal_cart_api, normal_user, temp_product):
        body = normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 2).json()

        with allure.step("断言数量是 2"):
            assert body["code"] == 200
            assert body["data"]["quantity"] == 2

    @allure.story("加入购物车")
    @allure.title("重复加入同一商品，数量自动累加")
    def test_add_same_product_twice(self, normal_cart_api, normal_user, temp_product):
        first = normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 2).json()
        assert first["code"] == 200

        second = normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1).json()

        with allure.step("断言两条记录合并成一条，数量变成 3"):
            assert second["code"] == 200
            assert second["data"]["quantity"] == 3

    @allure.story("查询购物车")
    @allure.title("查询用户购物车")
    def test_get_cart(self, normal_cart_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1)

        body = normal_cart_api.get_cart_by_user(normal_user["id"]).json()

        with allure.step("断言购物车里有商品"):
            assert body["code"] == 200
            assert len(body["data"]) == 1
            assert body["data"][0]["product"]["name"] == temp_product["name"]

    @allure.story("修改购物车")
    @allure.title("修改购物车商品数量")
    def test_update_quantity(self, normal_cart_api, normal_user, temp_product):
        added = normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1).json()
        cart_item_id = added["data"]["id"]

        body = normal_cart_api.update_quantity(cart_item_id, 5).json()

        with allure.step("断言数量改成 5"):
            assert body["code"] == 200
            assert body["data"]["quantity"] == 5

    @allure.story("删除购物车")
    @allure.title("按购物车项 ID 删除")
    def test_delete_cart_item(self, normal_cart_api, normal_user, temp_product):
        added = normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1).json()
        cart_item_id = added["data"]["id"]

        body = normal_cart_api.delete_cart_item(cart_item_id).json()

        with allure.step("断言删除成功，购物车为空"):
            assert body["code"] == 200
            cart = normal_cart_api.get_cart_by_user(normal_user["id"]).json()
            assert len(cart["data"]) == 0

    @allure.story("删除购物车")
    @allure.title("按用户 + 商品删除")
    def test_delete_by_user_and_product(self, normal_cart_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1)

        body = normal_cart_api.delete_by_user_and_product(
            normal_user["id"], temp_product["id"]
        ).json()

        with allure.step("断言删除成功"):
            assert body["code"] == 200
            cart = normal_cart_api.get_cart_by_user(normal_user["id"]).json()
            assert len(cart["data"]) == 0

    @allure.story("删除购物车")
    @allure.title("清空用户购物车")
    def test_clear_cart(self, normal_cart_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 2)

        body = normal_cart_api.clear_cart(normal_user["id"]).json()

        with allure.step("断言清空成功"):
            assert body["code"] == 200
            assert len(normal_cart_api.get_cart_by_user(normal_user["id"]).json()["data"]) == 0
