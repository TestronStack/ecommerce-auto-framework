from config.settings import BASE_URL


class OrdersPage:
    """我的订单页"""

    def __init__(self, page):
        self.page = page
        self.url = BASE_URL + "/orders.html"

    def open(self):
        self.page.goto(self.url)

    def paid_badge(self):
        # 找到状态文字是“已付款”的订单卡片标签
        return self.page.locator(".status-badge").filter(has_text="已付款").first
