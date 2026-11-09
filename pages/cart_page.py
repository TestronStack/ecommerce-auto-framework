from playwright.sync_api import expect

from config.settings import BASE_URL


class CartPage:
    """购物车页"""

    def __init__(self, page):
        self.page = page
        self.url = BASE_URL + "/cart.html"

    def open(self):
        self.page.goto(self.url)

    def clear_cart(self):
        """购物车不为空时点“清空购物车”"""
        if self.page.locator("#clear-cart-btn").is_visible():
            self.page.locator("#clear-cart-btn").click()
            # 清空后页面会显示“购物车是空的”
            expect(self.page.locator(".empty-state")).to_be_visible()

    def checkout(self):
        self.page.click("#checkout-btn")
