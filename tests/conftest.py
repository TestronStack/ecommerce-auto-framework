import json
import os
import random
import time

import pytest

from api.cart_api import CartApi
from api.category_api import CategoryApi
from api.order_api import OrderApi
from api.product_api import ProductApi
from api.review_api import ReviewApi
from api.user_api import UserApi
from config.settings import ADMIN_PASSWORD, ADMIN_USERNAME, AUTH_STATE_FILE, DATA_DIR


def unique_name(prefix="user"):
    """时间戳 + 随机数，保证每次生成的名字不重复（用户名限制 4-20 位）"""
    return prefix[:4] + "_" + str(int(time.time())) + str(random.randint(10, 99))


def load_json(file_name):
    """读取 data 目录下的 json 数据文件"""
    with open(os.path.join(DATA_DIR, file_name), encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------
# 登录态：整个测试会话只登录一次，所有接口复用 token
# ------------------------------------------------------------------

@pytest.fixture(scope="session")
def admin_token():
    """管理员登录，拿 token"""
    body = UserApi().login(ADMIN_USERNAME, ADMIN_PASSWORD).json()
    assert body["code"] == 200, "管理员登录失败：" + str(body)
    return body["data"]["token"]


@pytest.fixture(scope="session")
def user_api(admin_token):
    return UserApi(admin_token)


@pytest.fixture(scope="session")
def product_api(admin_token):
    return ProductApi(admin_token)


@pytest.fixture(scope="session")
def category_api(admin_token):
    return CategoryApi(admin_token)


@pytest.fixture(scope="session")
def cart_api(admin_token):
    return CartApi(admin_token)


@pytest.fixture(scope="session")
def order_api(admin_token):
    return OrderApi(admin_token)


@pytest.fixture(scope="session")
def review_api(admin_token):
    return ReviewApi(admin_token)


@pytest.fixture(scope="session")
def normal_user():
    """注册一个普通用户并登录，返回 id/token/用户名等信息"""
    username = unique_name("normal")
    password = "123456"
    email = username + "@test.com"

    register = UserApi().register(username, password, email)
    assert register.json()["code"] == 200, "普通用户注册失败：" + register.text

    login = UserApi().login(username, password).json()
    assert login["code"] == 200, "普通用户登录失败：" + str(login)

    return {
        "id": login["data"]["user"]["id"],
        "username": username,
        "password": password,
        "email": email,
        "token": login["data"]["token"],
    }


@pytest.fixture(scope="session")
def normal_cart_api(normal_user):
    """普通用户的购物车接口对象（购物车用例用自己的账号，避免和管理员数据混在一起）"""
    return CartApi(normal_user["token"])


@pytest.fixture(scope="session")
def normal_order_api(normal_user):
    return OrderApi(normal_user["token"])


@pytest.fixture
def role_token(request, admin_token, normal_user):
    """权限用例用：indirect 参数传 'admin' 或 'user'，返回对应 token"""
    return admin_token if request.param == "admin" else normal_user["token"]


# ------------------------------------------------------------------
# 测试数据：每个用例独立创建，用完清理
# ------------------------------------------------------------------

@pytest.fixture
def temp_user(admin_token):
    """用例专用的临时用户"""
    username = unique_name("tmp")
    password = "123456"
    email = username + "@test.com"

    body = UserApi().register(username, password, email).json()
    assert body["code"] == 200, "临时用户创建失败：" + str(body)
    info = body["data"]

    yield {
        "id": info["id"],
        "username": username,
        "password": password,
        "email": email,
    }

    # 清理：用户不存在时删除会返回 404，忽略即可
    UserApi(admin_token).delete_user(info["id"])


@pytest.fixture(scope="session")
def default_category_id(admin_token):
    """取一个可用分类 id，没有就创建一个"""
    body = CategoryApi(admin_token).get_all_categories().json()
    if body["code"] == 200 and body["data"]:
        return body["data"][0]["id"]

    created = CategoryApi(admin_token).create_category(unique_name("cate")).json()
    return created["data"]["id"]


@pytest.fixture
def temp_product(admin_token, default_category_id):
    """用例专用的临时商品，避免消耗示例商品的库存"""
    name = unique_name("goods")
    price = 99.9
    stock = 100

    body = ProductApi(admin_token).create_product(
        name, price, stock, description="自动化测试商品", category_id=default_category_id
    ).json()
    assert body["code"] == 200, "临时商品创建失败：" + str(body)
    product = body["data"]

    yield {
        "id": product["id"],
        "name": name,
        "price": price,
        "stock": stock,
        "category_id": default_category_id,
    }

    # 清理：商品可能已被订单引用，删除失败也不影响用例结果
    ProductApi(admin_token).delete_product(product["id"])


@pytest.fixture
def temp_category(admin_token):
    """用例专用的临时分类"""
    name = unique_name("cate")
    body = CategoryApi(admin_token).create_category(name, description="自动化测试分类").json()
    assert body["code"] == 200, "临时分类创建失败：" + str(body)
    category = body["data"]

    yield {"id": category["id"], "name": name}

    CategoryApi(admin_token).delete_category(category["id"])


# ------------------------------------------------------------------
# UI 自动化：复用 auth_state.json 里的登录态
# ------------------------------------------------------------------

@pytest.fixture(scope="session")
def logged_in_page(browser):
    """直接带着已登录的 storage_state 打开浏览器，整个会话只登录一次"""
    if not os.path.exists(AUTH_STATE_FILE):
        pytest.skip("没有登录态文件，请先执行：python tests/create_auth_state.py")

    context = browser.new_context(storage_state=AUTH_STATE_FILE)
    page = context.new_page()
    yield page
    context.close()
