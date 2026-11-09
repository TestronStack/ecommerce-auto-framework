import random
import time

import allure
import pytest

from api.cart_api import CartApi
from api.order_api import OrderApi
from api.product_api import ProductApi
from api.review_api import ReviewApi
from api.user_api import UserApi


def name_with_length(length, prefix="u"):
    """生成指定长度的名字，用时间戳保证每次不重复"""
    ts = str(int(time.time()))
    if length > len(ts):
        return prefix * (length - len(ts)) + ts
    if length == 1:
        return "b"
    return "b" + ts[-(length - 1):]


def random_name(prefix="e"):
    """普通随机名字：前缀 + 时间戳后 6 位 + 2 位随机数"""
    return prefix + str(int(time.time()))[-6:] + str(random.randint(10, 99))


@allure.feature("注册边界")
class TestRegisterBoundary:

    @allure.title("用户名长度边界：{length} 位，预期 {expect_code}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("length, expect_code", [(3, 400), (4, 200), (20, 200), (21, 400)])
    def test_username_length(self, user_api, length, expect_code):
        username = name_with_length(length)

        body = UserApi().register(username, "123456", username + "@t.com").json()

        with allure.step(f"断言 {length} 位用户名的注册结果"):
            assert body["code"] == expect_code

        if expect_code == 200:
            # 注册成功的数据用管理员清理
            user_api.delete_user(body["data"]["id"])

    @allure.title("密码长度边界：{pwd_length} 位，预期 {expect_code}")
    @pytest.mark.parametrize("pwd_length, expect_code", [(5, 400), (6, 200)])
    def test_password_length(self, user_api, pwd_length, expect_code):
        username = "pw" + str(pwd_length) + str(int(time.time()))[-6:]

        body = UserApi().register(username, "p" * pwd_length, username + "@t.com").json()

        assert body["code"] == expect_code
        if expect_code == 400:
            assert body["msg"] == "密码长度不能少于6个字符"
        else:
            user_api.delete_user(body["data"]["id"])

    @allure.title("邮箱格式非法：{email}")
    @pytest.mark.parametrize("email", ["bad-email", "a@", "@b.com", "a b@t.com"])
    def test_email_format(self, email):
        username = random_name("em")

        body = UserApi().register(username, "123456", email).json()

        assert body["code"] == 400
        assert body["msg"] == "邮箱格式不正确"

    @allure.title("邮箱为空，注册失败")
    def test_email_empty(self):
        username = random_name("em")

        body = UserApi().register(username, "123456", "").json()

        assert body["code"] == 400
        assert body["msg"] == "邮箱不能为空"

    @allure.title("邮箱重复，注册失败")
    def test_email_duplicate(self, user_api):
        suffix = str(int(time.time()))[-6:]
        email = "same" + suffix + "@t.com"

        first = UserApi().register("ea" + suffix, "123456", email).json()
        assert first["code"] == 200

        second = UserApi().register("eb" + suffix, "123456", email).json()

        with allure.step("断言重复邮箱被拒绝"):
            assert second["code"] == 400
            assert second["msg"] == "邮箱已存在"

        user_api.delete_user(first["data"]["id"])

    @allure.title("用户名和密码都为空，注册失败")
    def test_username_and_password_empty(self):
        body = UserApi().register("", "", "empty@t.com").json()

        assert body["code"] == 400


@allure.feature("商品边界")
class TestProductBoundary:

    @allure.title("商品价格边界：{price} 元，预期 {expect_code}")
    @pytest.mark.parametrize("price, expect_code", [(-1, 400), (0, 200)])
    def test_price(self, product_api, price, expect_code):
        name = random_name("pr")

        body = product_api.create_product(name, price, 10).json()

        with allure.step("断言价格边界结果"):
            assert body["code"] == expect_code
        if expect_code == 200:
            # 0 元商品属于合法边界值，创建后清理掉
            product_api.delete_product(body["data"]["id"])

    @allure.title("商品库存边界：{stock} 件，预期 {expect_code}")
    @pytest.mark.parametrize("stock, expect_code", [(-1, 400), (0, 200)])
    def test_stock(self, product_api, stock, expect_code):
        name = random_name("st")

        body = product_api.create_product(name, 10, stock).json()

        assert body["code"] == expect_code
        if expect_code == 200:
            product_api.delete_product(body["data"]["id"])

    @allure.title("商品名称长度边界：{length} 位，预期 {expect_code}")
    @pytest.mark.parametrize("length, expect_code", [(1, 400), (2, 200), (100, 200), (101, 400)])
    def test_name_length(self, product_api, length, expect_code):
        name = name_with_length(length, prefix="n")

        body = product_api.create_product(name, 10, 10).json()

        assert body["code"] == expect_code
        if expect_code == 200:
            product_api.delete_product(body["data"]["id"])

    @allure.title("必填字段缺失：{field}")
    @pytest.mark.parametrize("field", ["name", "price", "stock"])
    def test_required_field_missing(self, product_api, field):
        # 缺哪个字段就把哪个字段去掉
        payload = {"name": random_name("req"), "price": 10, "stock": 5}
        payload.pop(field)

        body = product_api.post("/product", json=payload).json()

        with allure.step("断言提示对应的必填字段"):
            assert body["code"] == 400
            assert "不能为空" in body["msg"]

    @allure.title("商品描述长度 500 字（已知缺陷：数据库列存不下）")
    @pytest.mark.xfail(reason="已知缺陷：@Size 允许 500 字，但数据库 description 列长度不足，返回 500",
                       strict=True)
    def test_description_500(self, product_api):
        body = product_api.post("/product", json={
            "name": random_name("desc"), "price": 1, "stock": 1, "description": "d" * 500
        }).json()

        # 期望按校验规则正常创建
        assert body["code"] == 200


@allure.feature("购物车边界")
class TestCartBoundary:

    @pytest.fixture(autouse=True)
    def clean_cart(self, normal_cart_api, normal_user):
        normal_cart_api.clear_cart(normal_user["id"])
        yield

    @allure.title("加购数量边界：{quantity}，预期 {expect_code}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("quantity, expect_code", [(0, 400), (-1, 400)])
    def test_quantity(self, normal_cart_api, normal_user, temp_product, quantity, expect_code):
        body = normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], quantity).json()

        assert body["code"] == expect_code
        assert body["msg"] == "数量不能少于1"

    @allure.title("加购不传数量，返回 400")
    def test_quantity_missing(self, normal_cart_api, normal_user, temp_product):
        body = normal_cart_api.post(
            "/cart", json={"user": {"id": normal_user["id"]}, "product": {"id": temp_product["id"]}}
        ).json()

        assert body["code"] == 400
        assert body["msg"] == "数量不能为空"

    @allure.title("修改数量为 0，返回 400")
    def test_update_quantity_zero(self, normal_cart_api, normal_user, temp_product):
        added = normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1).json()

        body = normal_cart_api.update_quantity(added["data"]["id"], 0).json()

        assert body["code"] == 400
        assert body["msg"] == "数量不能少于1"

    @allure.title("加购数量超过库存（加购不校验库存，下单时才校验）")
    def test_quantity_over_stock(self, normal_cart_api, normal_user, temp_product):
        body = normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 999).json()

        with allure.step("断言加购阶段不拦截，只有下单时才校验库存"):
            assert body["code"] == 200
            assert body["data"]["quantity"] == 999

    @allure.title("加购不存在的商品（已知缺陷：返回 500）")
    @pytest.mark.xfail(reason="已知缺陷：加购不存在的商品返回 500，应返回 404 商品不存在", strict=True)
    def test_product_not_exist(self, normal_cart_api, normal_user):
        body = normal_cart_api.add_to_cart(normal_user["id"], 999999, 1).json()

        assert body["code"] == 404


@allure.feature("订单边界")
class TestOrderBoundary:

    @pytest.fixture(autouse=True)
    def clean_cart(self, normal_cart_api, normal_user):
        normal_cart_api.clear_cart(normal_user["id"])
        yield

    @allure.title("购物车为空时下单，返回 400")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_empty_cart(self, normal_order_api, normal_user):
        body = normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        ).json()

        assert body["code"] == 400
        assert body["msg"] == "购物车为空"

    @allure.title("下单用户不存在，返回 404")
    def test_user_not_exist(self, normal_order_api):
        body = normal_order_api.create_order_from_cart(
            999999, "张三", "13800001111", "深圳市南山区"
        ).json()

        assert body["code"] == 404
        assert body["msg"] == "用户不存在"

    @allure.title("加购数量超过库存，下单返回 400 库存不足")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_stock_not_enough(self, product_api, normal_cart_api, normal_order_api, normal_user):
        # 专门建一个库存只有 1 件的商品
        created = product_api.create_product(random_name("low"), 10, 1).json()
        product_id = created["data"]["id"]

        normal_cart_api.add_to_cart(normal_user["id"], product_id, 5)

        body = normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        ).json()

        with allure.step("断言库存不足被拦截"):
            assert body["code"] == 400
            assert body["msg"] == "库存不足"

        product_api.delete_product(product_id)

    @allure.title("直接下单：数量为 0，返回 400")
    def test_create_order_quantity_zero(self, normal_order_api, normal_user, temp_product):
        # 直接下单必须自己传 totalAmount，否则会提示订单金额不能为空
        body = normal_order_api.post("/order", json={
            "user": {"id": normal_user["id"]},
            "totalAmount": 0,
            "orderItems": [{"product": {"id": temp_product["id"]}, "quantity": 0}],
        }).json()

        assert body["code"] == 400
        assert body["msg"] == "数量不能少于1"

    @allure.title("直接下单：商品不存在（已知缺陷：返回 500）")
    @pytest.mark.xfail(reason="已知缺陷：下单不存在的商品返回 500，应返回 404 商品不存在", strict=True)
    def test_create_order_product_not_exist(self, normal_order_api, normal_user):
        body = normal_order_api.post("/order", json={
            "user": {"id": normal_user["id"]},
            "totalAmount": 20,
            "orderItems": [{"product": {"id": 999999}, "quantity": 1}],
        }).json()

        assert body["code"] == 404

    @allure.title("更新订单状态：订单不存在，返回 404")
    def test_update_status_order_not_exist(self, normal_order_api):
        body = normal_order_api.update_order_status(999999, "PAID").json()

        assert body["code"] == 404
        assert body["msg"] == "订单不存在"

    @allure.title("更新订单状态为非法值 ABC（已知缺陷：没有枚举校验）")
    @pytest.mark.xfail(reason="已知缺陷：订单状态没有枚举校验，传 ABC 也会更新成功", strict=True)
    def test_update_status_invalid(self, normal_cart_api, normal_order_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1)
        created = normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        ).json()
        order_id = created["data"]["id"]

        body = normal_order_api.update_order_status(order_id, "ABC").json()

        assert body["code"] == 400

    @allure.title("更新支付状态为非法值 ABC（已知缺陷：没有枚举校验）")
    @pytest.mark.xfail(reason="已知缺陷：支付状态没有枚举校验，传 ABC 也会更新成功", strict=True)
    def test_update_payment_status_invalid(self, normal_cart_api, normal_order_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1)
        created = normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        ).json()
        order_id = created["data"]["id"]

        body = normal_order_api.update_payment_status(order_id, "ABC").json()

        assert body["code"] == 400

    @allure.title("更新订单状态不传 status 参数（已知缺陷：返回 500）")
    @pytest.mark.xfail(reason="已知缺陷：缺少必填参数时返回 500，应返回 400", strict=True)
    def test_update_status_param_missing(self, normal_cart_api, normal_order_api, normal_user, temp_product):
        normal_cart_api.add_to_cart(normal_user["id"], temp_product["id"], 1)
        created = normal_order_api.create_order_from_cart(
            normal_user["id"], "张三", "13800001111", "深圳市南山区"
        ).json()
        order_id = created["data"]["id"]

        body = normal_order_api.put("/order/" + str(order_id) + "/status").json()

        assert body["code"] == 400


@allure.feature("评价边界")
class TestReviewBoundary:

    @allure.title("评分边界：{rating} 分，预期 {expect_code}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("rating, expect_code", [(0, 400), (1, 200), (5, 200), (6, 400)])
    def test_rating(self, review_api, normal_user, temp_product, rating, expect_code):
        body = review_api.create_review(normal_user["id"], temp_product["id"], rating, "评分边界测试").json()

        with allure.step("断言评分边界结果"):
            assert body["code"] == expect_code
        if expect_code == 400:
            assert ("1分" in body["msg"]) or ("5分" in body["msg"])
        else:
            review_api.delete_review(body["data"]["id"])

    @allure.title("评价内容为空，返回 400")
    def test_content_empty(self, review_api, normal_user, temp_product):
        body = review_api.create_review(normal_user["id"], temp_product["id"], 5, "").json()

        assert body["code"] == 400
        assert body["msg"] == "评价内容不能为空"

    @allure.title("不传评分，返回 400")
    def test_rating_missing(self, review_api, normal_user, temp_product):
        body = review_api.post("/review", json={
            "user": {"id": normal_user["id"]},
            "product": {"id": temp_product["id"]},
            "content": "没有评分",
        }).json()

        assert body["code"] == 400
        assert body["msg"] == "评分不能为空"

    @allure.title("更新评价时评分传 0，返回 400")
    def test_update_rating_zero(self, review_api, normal_user, temp_product):
        created = review_api.create_review(normal_user["id"], temp_product["id"], 5, "原评价").json()
        review_id = created["data"]["id"]

        body = review_api.update_review(
            review_id, normal_user["id"], temp_product["id"], 0, "改成0分"
        ).json()

        assert body["code"] == 400
        assert body["msg"] == "评分不能低于1分"

        review_api.delete_review(review_id)


@allure.feature("查询边界")
class TestQueryBoundary:

    @allure.title("分页参数 size=1000 超出常规值")
    def test_page_size_1000(self, product_api):
        body = product_api.page_products(page=0, size=1000).json()

        assert body["code"] == 200
        assert isinstance(body["data"]["content"], list)

    @allure.title("分页参数 size=0（Spring 忽略 0，按默认值 20 返回）")
    def test_page_size_zero(self, product_api):
        body = product_api.page_products(page=0, size=0).json()

        with allure.step("断言不报错，最多返回默认的 20 条"):
            assert body["code"] == 200
            assert len(body["data"]["content"]) <= 20

    @allure.title("分页参数 page=-1（Spring 不报错，正常返回）")
    def test_page_negative(self, product_api):
        body = product_api.page_products(page=-1, size=10).json()

        assert body["code"] == 200

    @allure.title("排序字段不存在（已知缺陷：返回 500）")
    @pytest.mark.xfail(reason="已知缺陷：非法排序字段返回 500，应返回 400 参数错误", strict=True)
    def test_sort_invalid(self, product_api):
        body = product_api.get("/product/page", params={"page": 0, "size": 5, "sort": "abc,desc"}).json()

        assert body["code"] == 400

    @allure.title("价格区间 min > max，返回空列表")
    def test_price_range_reversed(self, product_api):
        body = product_api.get_products_by_price_range(500, 100).json()

        with allure.step("断言不报错，返回空列表"):
            assert body["code"] == 200
            assert body["data"] == []

    @allure.title("价格区间传负数，返回 400")
    def test_price_range_negative(self, product_api):
        body = product_api.get_products_by_price_range(-1, 10).json()

        assert body["code"] == 400
        assert body["msg"] == "最小不能小于0"

    @allure.title("路径参数类型错误：用户 ID 传 abc")
    def test_user_id_type_error(self, user_api):
        body = user_api.get_user_by_id("abc").json()

        assert body["code"] == 400
        assert body["msg"] == "参数类型错误：id"

    @allure.title("路径参数类型错误：商品 ID 传 abc")
    def test_product_id_type_error(self, product_api):
        body = product_api.get_product_by_id("abc").json()

        assert body["code"] == 400
        assert body["msg"] == "参数类型错误：id"
