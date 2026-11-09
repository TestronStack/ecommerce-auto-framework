from api.base_api import BaseApi


class ReviewApi(BaseApi):
    """评价模块：9 个接口"""

    def create_review(self, user_id, product_id, rating, content):
        body = {
            "user": {"id": user_id},
            "product": {"id": product_id},
            "rating": rating,
            "content": content,
        }
        return self.post("/review", json=body)

    def get_all_reviews(self):
        return self.get("/review")

    def get_reviews_by_product(self, product_id):
        return self.get("/review/product/" + str(product_id))

    def get_active_reviews_by_product(self, product_id):
        return self.get("/review/product/" + str(product_id) + "/active")

    def get_reviews_by_user(self, user_id):
        return self.get("/review/user/" + str(user_id))

    def get_reviews_by_rating(self, rating):
        return self.get("/review/rating/" + str(rating))

    def get_review_by_id(self, review_id):
        return self.get("/review/id/" + str(review_id))

    def update_review(self, review_id, user_id, product_id, rating, content):
        body = {
            "user": {"id": user_id},
            "product": {"id": product_id},
            "rating": rating,
            "content": content,
        }
        return self.put("/review/" + str(review_id), json=body)

    def delete_review(self, review_id):
        return self.delete("/review/" + str(review_id))
