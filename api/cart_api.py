from api.base_api import BaseApi


class CartApi(BaseApi):
    """购物车模块：6 个接口"""

    def add_to_cart(self, user_id, product_id, quantity=1):
        body = {
            "user": {"id": user_id},
            "product": {"id": product_id},
            "quantity": quantity,
        }
        return self.post("/cart", json=body)

    def get_cart_by_user(self, user_id):
        return self.get("/cart/user/" + str(user_id))

    def update_quantity(self, cart_item_id, quantity):
        # 只传 quantity，用户和商品沿用原记录
        return self.put("/cart/" + str(cart_item_id), json={"quantity": quantity})

    def delete_cart_item(self, cart_item_id):
        return self.delete("/cart/" + str(cart_item_id))

    def delete_by_user_and_product(self, user_id, product_id):
        return self.delete("/cart/user/" + str(user_id) + "/product/" + str(product_id))

    def clear_cart(self, user_id):
        return self.delete("/cart/user/" + str(user_id))
