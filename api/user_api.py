from api.base_api import BaseApi


class UserApi(BaseApi):
    """用户模块：8 个接口"""

    def register(self, username, password, email, phone=None, address=None):
        body = {"username": username, "password": password, "email": email}
        if phone:
            body["phone"] = phone
        if address:
            body["address"] = address
        return self.post("/user/register", json=body)

    def login(self, username, password):
        return self.post("/user/login", json={"username": username, "password": password})

    def get_all_users(self):
        return self.get("/user")

    def page_users(self, page=0, size=5, sort="id,desc"):
        params = {"page": page, "size": size, "sort": sort}
        return self.get("/user/page", params=params)

    def get_user_by_id(self, user_id):
        return self.get("/user/id/" + str(user_id))

    def get_user_by_username(self, username):
        return self.get("/user/username/" + username)

    def update_user(self, user_id, payload):
        return self.put("/user/" + str(user_id), json=payload)

    def delete_user(self, user_id):
        return self.delete("/user/" + str(user_id))
