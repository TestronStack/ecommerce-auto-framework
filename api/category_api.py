from api.base_api import BaseApi


class CategoryApi(BaseApi):
    """分类模块：8 个接口"""

    def create_category(self, name, description=None, parent_id=None, sort=0):
        body = {"name": name, "sort": sort, "status": 1}
        if description:
            body["description"] = description
        if parent_id:
            body["parent"] = {"id": parent_id}
        return self.post("/category", json=body)

    def get_all_categories(self):
        return self.get("/category")

    def get_category_by_id(self, category_id):
        return self.get("/category/id/" + str(category_id))

    def get_top_categories(self):
        return self.get("/category/top")

    def get_child_categories(self, parent_id):
        return self.get("/category/child/" + str(parent_id))

    def get_active_categories(self):
        return self.get("/category/active")

    def update_category(self, category_id, payload):
        return self.put("/category/" + str(category_id), json=payload)

    def delete_category(self, category_id):
        return self.delete("/category/" + str(category_id))
