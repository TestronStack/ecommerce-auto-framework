from api.base_api import BaseApi


class OrderApi(BaseApi):
    """订单模块：10 个接口"""

    def create_order(self, user_id, order_items):
        # order_items 格式：[{"product": {"id": 1}, "quantity": 2}]
        body = {"user": {"id": user_id}, "orderItems": order_items}
        return self.post("/order", json=body)

    def create_order_from_cart(self, user_id, shipping_name, shipping_phone,
                               shipping_address, payment_method="ALIPAY"):
        body = {
            "shippingName": shipping_name,
            "shippingPhone": shipping_phone,
            "shippingAddress": shipping_address,
            "paymentMethod": payment_method,
        }
        return self.post("/order/from-cart/" + str(user_id), json=body)

    def page_orders(self, page=0, size=10, sort="id,desc"):
        params = {"page": page, "size": size, "sort": sort}
        return self.get("/order/page", params=params)

    def get_orders_by_user(self, user_id):
        return self.get("/order/user/" + str(user_id))

    def get_order_by_id(self, order_id):
        return self.get("/order/id/" + str(order_id))

    def get_orders_by_status(self, status):
        return self.get("/order/status/" + status)

    def get_orders_by_payment_status(self, payment_status):
        return self.get("/order/payment-status/" + payment_status)

    def get_order_by_number(self, order_number):
        return self.get("/order/order-number/" + order_number)

    def update_order_status(self, order_id, status):
        return self.put("/order/" + str(order_id) + "/status", params={"status": status})

    def update_payment_status(self, order_id, payment_status):
        return self.put("/order/" + str(order_id) + "/payment-status",
                        params={"paymentStatus": payment_status})
