import allure
import pytest

from tests.conftest import load_json


@allure.feature("订单模块")
class TestOrder:

    @pytest.fixture(autouse=True)
    def clean_cart(self, normal_cart_api, normal_user):
        """每个用例开始前清空购物车"""
        normal_cart_api.clear_cart(normal_user["id"])
        yield

    @allure.story("下单")
    @allure.title("购物车一键下单成功")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_order_from_cart(self, normal_cart_api, normal_order_api, normal_user, temp_product):
        shipping = load_json("order_data.json")["shipping"]

        # 先加 3 件到购物车
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 3)

        body = normal_order_api.create_order_from_cart(
            normal_user["id"],
            shipping["shippingName"],
            shipping["shippingPhone"],
            shipping["shippingAddress"],
            shipping["paymentMethod"],
        ).json()

        with allure.step("断言订单生成成功"):
            assert body["code"] == 200
            order = body["data"]
            assert order["status"] == "PENDING"
            assert order["paymentStatus"] == "UNPAID"
            assert order["shippingName"] == shipping["shippingName"]
            assert order["orderNumber"].startswith("ORDER_")

        with allure.step("断言金额 = 单价 × 数量"):
            expected = temp_product["price"] * 3
            assert order["totalAmount"] == pytest.approx(expected, abs=0.01)

        with allure.step("断言购物车已被清空"):
            cart = normal_cart_api.get_cart_by_user(normal_user["id"]).json()
            assert len(cart["data"]) == 0

    @allure.story("下单")
    @allure.title("购物车为空时下单失败，返回 400")
    def test_create_order_with_empty_cart(self, normal_order_api, normal_user):
        body = normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        ).json()

        assert body["code"] == 400
        assert body["msg"] == "购物车为空"

    @allure.story("查询订单")
    @allure.title("查询用户订单列表")
    def test_get_orders_by_user(self, normal_cart_api, normal_order_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1)
        normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        )

        body = normal_order_api.get_orders_by_user(normal_user["id"]).json()

        with allure.step("断言能查到订单，且含订单明细"):
            assert body["code"] == 200
            assert len(body["data"]) >= 1
            assert len(body["data"][0]["orderItems"]) >= 1

    @allure.story("查询订单")
    @allure.title("按 ID 查询订单")
    def test_get_order_by_id(self, normal_cart_api, normal_order_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1)
        created = normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        ).json()
        order_id = created["data"]["id"]

        body = normal_order_api.get_order_by_id(order_id).json()

        assert body["code"] == 200
        assert body["data"]["id"] == order_id

    @allure.story("查询订单")
    @allure.title("按订单号查询订单")
    def test_get_order_by_number(self, normal_cart_api, normal_order_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1)
        created = normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        ).json()
        order_number = created["data"]["orderNumber"]

        body = normal_order_api.get_order_by_number(order_number).json()

        assert body["code"] == 200
        assert body["data"]["orderNumber"] == order_number

    @allure.story("查询订单")
    @allure.title("查询不存在的订单，返回 404")
    def test_get_order_not_exist(self, normal_order_api):
        body = normal_order_api.get_order_by_id(999999).json()

        assert body["code"] == 404
        assert body["msg"] == "订单不存在"

    @allure.story("查询订单")
    @allure.title("按状态查询订单")
    def test_get_orders_by_status(self, normal_order_api):
        body = normal_order_api.get_orders_by_status("PAID").json()

        assert body["code"] == 200
        for order in body["data"]:
            assert order["status"] == "PAID"

    @allure.story("查询订单")
    @allure.title("分页查询订单")
    def test_page_orders(self, normal_order_api):
        body = normal_order_api.page_orders(page=0, size=10).json()

        assert body["code"] == 200
        assert body["data"]["number"] == 0

    @allure.story("支付订单")
    @allure.title("支付订单后，订单状态自动变成 PAID")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_pay_order(self, normal_cart_api, normal_order_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1)
        created = normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        ).json()
        order_id = created["data"]["id"]

        body = normal_order_api.update_payment_status(order_id, "PAID").json()

        with allure.step("断言支付状态和订单状态都变了"):
            assert body["code"] == 200
            assert body["data"]["paymentStatus"] == "PAID"
            assert body["data"]["status"] == "PAID"
            assert body["data"]["paidAt"] is not None

    @allure.story("订单状态流转")
    @allure.title("确认收货后，订单状态变成 DELIVERED")
    def test_update_order_status(self, normal_cart_api, normal_order_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1)
        created = normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        ).json()
        order_id = created["data"]["id"]

        body = normal_order_api.update_order_status(order_id, "DELIVERED").json()

        with allure.step("断言状态和收货时间"):
            assert body["code"] == 200
            assert body["data"]["status"] == "DELIVERED"
            assert body["data"]["deliveredAt"] is not None
