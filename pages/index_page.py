from config.settings import BASE_URL


class IndexPage:
    """首页商品列表"""

    def __init__(self, page):
        self.page = page
        self.url = BASE_URL + "/index.html"

    def open(self):
        self.page.goto(self.url)

    def add_first_product_to_cart(self):
        # 第一个商品的“加入购物车”按钮
        self.page.locator(".add-cart-btn").first.click()

    def cart_badge(self):
        return self.page.locator("#cart-badge")

    def search(self, keyword):
        self.page.fill("#search-input", keyword)
        self.page.click("#search-btn")
