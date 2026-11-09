import allure
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.index_page import IndexPage
from pages.orders_page import OrdersPage


@allure.feature("UI 自动化")
class TestUiShopFlow:

    @allure.title("已登录用户：浏览商品 -> 加购 -> 结算 -> 支付")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_ui_buy_product(self, logged_in_page):
        page = logged_in_page
        cart = CartPage(page)
        index = IndexPage(page)

        with allure.step("先把购物车清空，保证用例起点干净"):
            cart.open()
            cart.clear_cart()

        with allure.step("打开首页，加入购物车"):
            index.open()
            expect(page.locator(".product-card").first).to_be_visible()
            index.add_first_product_to_cart()
            expect(index.cart_badge()).to_have_text("1")

        with allure.step("进入购物车，点击去结算"):
            cart.open()
            expect(page.locator(".cart-item").first).to_be_visible()
            cart.checkout()

        with allure.step("填写收货信息并提交订单"):
            checkout = CheckoutPage(page)
            expect(page.locator("#shipping-name")).to_be_visible()
            checkout.fill_shipping("张三", "13800001111", "深圳市南山区科技园")
            checkout.submit_order()
            order_number = checkout.order_number()
            assert order_number.startswith("ORDER_")

        with allure.step("点击立即支付"):
            checkout.pay()

        with allure.step("订单列表出现“已付款”的订单"):
            orders = OrdersPage(page)
            expect(orders.paid_badge()).to_be_visible()
