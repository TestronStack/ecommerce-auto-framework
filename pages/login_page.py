from config.settings import BASE_URL


class LoginPage:
    """登录页"""

    def __init__(self, page):
        self.page = page
        self.url = BASE_URL + "/login.html"

    def open(self):
        self.page.goto(self.url)

    def login(self, username, password):
        self.page.fill("#username", username)
        self.page.fill("#password", password)
        self.page.click("#login-btn")
