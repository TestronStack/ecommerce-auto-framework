from playwright.sync_api import expect

from config.settings import BASE_URL

class CheckoutPage:
    """结算页：填收货信息 -> 提交订单 -> 支付"""

    def __init__(self, page):
        self.page = page
        self.url = BASE_URL + "/checkout.html"

    def open(self):
        self.page.goto(self.url)

    def fill_shipping(self, name, phone, address, payment_method="ALIPAY"):
        self.page.fill("#shipping-name", name)
        self.page.fill("#shipping-phone", phone)
        self.page.fill("#shipping-address", address)
        self.page.select_option("#payment-method", payment_method)

    def submit_order(self):
        self.page.click("#submit-order-btn")
        # 提交成功后会出现支付卡片，里面有订单号
        expect(self.page.locator("#pay-box")).to_be_visible()

    def order_number(self):
        return self.page.locator("#pay-order-number").inner_text()

    def pay(self):
        self.page.click("#pay-now-btn")
        # 支付成功后页面会自动跳回订单列表
        self.page.wait_for_url("**/orders.html")
