import allure


@allure.feature("评价模块")
class TestReview:

    @allure.story("发表评价")
    @allure.title("发表商品评价成功")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_review(self, review_api, normal_user, temp_product):
        body = review_api.create_review(
            normal_user["id"], temp_product["id"], 5, "很好用，物流也快"
        ).json()

        with allure.step("断言评价创建成功"):
            assert body["code"] == 200
            assert body["data"]["rating"] == 5
            assert body["data"]["product"]["id"] == temp_product["id"]

    @allure.story("查询评价")
    @allure.title("查询商品评价，无评价时返回空数组")
    def test_get_reviews_empty(self, review_api, temp_product):
        body = review_api.get_reviews_by_product(temp_product["id"]).json()

        with allure.step("断言没有评价时返回空列表，而不是 404"):
            assert body["code"] == 200
            assert body["data"] == []

    @allure.story("查询评价")
    @allure.title("查询商品评价列表")
    def test_get_reviews_by_product(self, review_api, normal_user, temp_product):
        review_api.create_review(normal_user["id"], temp_product["id"], 4, "还不错")

        body = review_api.get_reviews_by_product(temp_product["id"]).json()

        assert body["code"] == 200
        assert len(body["data"]) == 1
        assert body["data"][0]["content"] == "还不错"

    @allure.story("查询评价")
    @allure.title("查询商品有效评价")
    def test_get_active_reviews(self, review_api, normal_user, temp_product):
        review_api.create_review(normal_user["id"], temp_product["id"], 5, "很满意")

        body = review_api.get_active_reviews_by_product(temp_product["id"]).json()

        assert body["code"] == 200
        for review in body["data"]:
            assert review["status"] == 1

    @allure.story("查询评价")
    @allure.title("查询所有评价")
    def test_get_all_reviews(self, review_api):
        body = review_api.get_all_reviews().json()

        assert body["code"] == 200
        assert isinstance(body["data"], list)

    @allure.story("查询评价")
    @allure.title("按用户查询评价")
    def test_get_reviews_by_user(self, review_api, normal_user, temp_product):
        review_api.create_review(normal_user["id"], temp_product["id"], 5, "用户评价")

        body = review_api.get_reviews_by_user(normal_user["id"]).json()

        assert body["code"] == 200
        assert len(body["data"]) >= 1

    @allure.story("查询评价")
    @allure.title("按评分查询评价")
    def test_get_reviews_by_rating(self, review_api, normal_user, temp_product):
        review_api.create_review(normal_user["id"], temp_product["id"], 3, "一般般")

        body = review_api.get_reviews_by_rating(3).json()

        assert body["code"] == 200
        for review in body["data"]:
            assert review["rating"] == 3

    @allure.story("更新评价")
    @allure.title("更新评价内容和评分")
    def test_update_review(self, review_api, normal_user, temp_product):
        created = review_api.create_review(
            normal_user["id"], temp_product["id"], 3, "原来的评价"
        ).json()
        review_id = created["data"]["id"]

        body = review_api.update_review(
            review_id, normal_user["id"], temp_product["id"], 5, "更新后的评价"
        ).json()

        with allure.step("断言评价已更新"):
            assert body["code"] == 200
            assert body["data"]["rating"] == 5
            assert body["data"]["content"] == "更新后的评价"

    @allure.story("删除评价")
    @allure.title("删除评价成功")
    def test_delete_review(self, review_api, normal_user, temp_product):
        created = review_api.create_review(
            normal_user["id"], temp_product["id"], 5, "这条评价要被删除"
        ).json()
        review_id = created["data"]["id"]

        body = review_api.delete_review(review_id).json()

        with allure.step("断言删除成功，再查返回 404"):
            assert body["code"] == 200
            assert review_api.get_review_by_id(review_id).json()["code"] == 404

    @allure.story("查询评价")
    @allure.title("按 ID 查询不存在的评价，返回 404")
    def test_get_review_not_exist(self, review_api):
        body = review_api.get_review_by_id(999999).json()

        assert body["code"] == 404
        assert body["msg"] == "评价不存在"
