import time

import allure

from api.cart_api import CartApi
from api.category_api import CategoryApi
from api.order_api import OrderApi
from api.product_api import ProductApi
from api.review_api import ReviewApi
from api.user_api import UserApi
from tests.conftest import load_json, unique_name


@allure.feature("完整业务流程")
@allure.story("注册 - 登录 - 浏览 - 加购 - 下单 - 支付 - 收货 - 评价")
class TestFullFlow:

    @allure.title("新用户走完整商城主流程")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_shop_flow(self, admin_token, default_category_id):
        shipping = load_json("order_data.json")["shipping"]

        # 准备：创建一个临时商品，并记录默认分类
        product_name = unique_name("flow_goods")
        ProductApi(admin_token).create_product(
            product_name, 199.0, 50, category_id=default_category_id
        )

        username = "flow_" + str(int(time.time()))
        email = username + "@test.com"

        with allure.step("1. 注册新用户"):
            register = UserApi().register(username, "123456", email, "13800001111").json()
            assert register["code"] == 200
            user_id = register["data"]["id"]

        with allure.step("2. 登录并拿到 token"):
            login = UserApi().login(username, "123456").json()
            assert login["code"] == 200
            token = login["data"]["token"]
            # 之后所有接口都用这个用户自己的 token
            user_api = UserApi(token)
            category_api = CategoryApi(token)
            product_api = ProductApi(token)
            cart_api = CartApi(token)
            order_api = OrderApi(token)
            review_api = ReviewApi(token)

        with allure.step("3. 查询分类"):
            categories = category_api.get_all_categories().json()
            assert categories["code"] == 200
            assert len(categories["data"]) > 0

        with allure.step("4. 查询商品列表"):
            products = product_api.get_all_products().json()
            assert products["code"] == 200
            # 找到刚才创建的商品
            my_product = None
            for product in products["data"]:
                if product["name"] == product_name:
                    my_product = product
                    break
            assert my_product is not None

        with allure.step("5. 加入购物车 2 件"):
            cart_api.add_to_cart(user_id, my_product["id"], 2)
            cart = cart_api.get_cart_by_user(user_id).json()
            assert len(cart["data"]) == 1
            assert cart["data"][0]["quantity"] == 2

        with allure.step("6. 重复加购 1 件，数量累加为 3"):
            cart_api.add_to_cart(user_id, my_product["id"], 1)
            cart = cart_api.get_cart_by_user(user_id).json()
            assert cart["data"][0]["quantity"] == 3
            cart_item_id = cart["data"][0]["id"]

        with allure.step("7. 修改购物车数量为 5"):
            cart_api.update_quantity(cart_item_id, 5)
            cart = cart_api.get_cart_by_user(user_id).json()
            assert cart["data"][0]["quantity"] == 5

        with allure.step("8. 提交订单"):
            order = order_api.create_order_from_cart(
                user_id,
                shipping["shippingName"],
                shipping["shippingPhone"],
                shipping["shippingAddress"],
                shipping["paymentMethod"],
            ).json()
            assert order["code"] == 200
            order_id = order["data"]["id"]
            order_number = order["data"]["orderNumber"]
            assert order["data"]["status"] == "PENDING"
            assert order["data"]["paymentStatus"] == "UNPAID"

        with allure.step("9. 校验订单金额"):
            order = order_api.get_order_by_id(order_id).json()["data"]
            assert order["totalAmount"] == 199.0 * 5
            # 明细字段是 unitPrice / totalPrice，不是 price
            item = order["orderItems"][0]
            assert item["unitPrice"] == 199.0
            assert item["totalPrice"] == 199.0 * 5

        with allure.step("10. 确认购物车已清空"):
            cart = cart_api.get_cart_by_user(user_id).json()
            assert len(cart["data"]) == 0

        with allure.step("11. 按订单号能查到订单"):
            by_number = order_api.get_order_by_number(order_number).json()
            assert by_number["code"] == 200
            assert by_number["data"]["id"] == order_id

        with allure.step("12. 支付订单"):
            paid = order_api.update_payment_status(order_id, "PAID").json()
            assert paid["code"] == 200
            assert paid["data"]["paymentStatus"] == "PAID"
            assert paid["data"]["status"] == "PAID"
            assert paid["data"]["paidAt"] is not None

        with allure.step("13. 确认收货"):
            delivered = order_api.update_order_status(order_id, "DELIVERED").json()
            assert delivered["code"] == 200
            assert delivered["data"]["status"] == "DELIVERED"
            assert delivered["data"]["deliveredAt"] is not None

        with allure.step("14. 发表评价"):
            review = review_api.create_review(user_id, my_product["id"], 5, "全流程测试评价").json()
            assert review["code"] == 200

        with allure.step("15. 查看商品评价"):
            reviews = review_api.get_reviews_by_product(my_product["id"]).json()
            assert reviews["code"] == 200
            assert len(reviews["data"]) == 1
            assert reviews["data"][0]["rating"] == 5

        with allure.step("16. 局部更新用户资料"):
            updated = user_api.update_user(user_id, {"address": "深圳市宝安区"}).json()
            assert updated["code"] == 200
            assert updated["data"]["address"] == "深圳市宝安区"
            # 其它字段不受影响
            assert updated["data"]["username"] == username

        with allure.step("17. 尝试清理测试数据（订单和用户有外键关联，删除失败可忽略）"):
            # 用户下过订单后就被订单引用了，删不掉是正常的业务约束
            UserApi(admin_token).delete_user(user_id)
            ProductApi(admin_token).delete_product(my_product["id"])
