from api.base_api import BaseApi


class ProductApi(BaseApi):
    """商品模块：11 个接口"""

    def create_product(self, name, price, stock, description=None, category_id=None, status=1):
        body = {"name": name, "price": price, "stock": stock, "status": status}
        if description:
            body["description"] = description
        if category_id:
            body["category"] = {"id": category_id}
        return self.post("/product", json=body)

    def get_all_products(self):
        return self.get("/product")

    def page_products(self, page=0, size=10, sort="id,desc"):
        params = {"page": page, "size": size, "sort": sort}
        return self.get("/product/page", params=params)

    def get_product_by_id(self, product_id):
        return self.get("/product/id/" + str(product_id))

    def get_products_by_category(self, category_id):
        return self.get("/product/category/" + str(category_id))

    def get_products_by_status(self, status):
        return self.get("/product/status/" + str(status))

    def search_products(self, name):
        return self.get("/product/search", params={"name": name})

    def get_products_by_price_range(self, min_price, max_price):
        params = {"minPrice": min_price, "maxPrice": max_price}
        return self.get("/product/price-range", params=params)

    def update_product(self, product_id, payload):
        return self.put("/product/" + str(product_id), json=payload)

    def delete_product(self, product_id):
        return self.delete("/product/" + str(product_id))

    def upload_image(self, file_path):
        # 上传图片是 multipart/form-data，和普通 json 请求不一样
        with open(file_path, "rb") as f:
            files = {"file": f}
            return self.session.post(self.base_url + "/product/upload-image", files=files)
