"""用 Playwright 登录一次，把登录态保存到 tests/auth_state.json。
只需在第一次运行 UI 用例前执行一次：

    python tests/create_auth_state.py
"""

import os
import sys

# 直接 python 运行本脚本时，要先把项目根目录加入路径，否则找不到 config 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import expect, sync_playwright

from config.settings import ADMIN_PASSWORD, ADMIN_USERNAME, AUTH_STATE_FILE, BASE_URL


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(BASE_URL + "/login.html")
        page.fill("#username", ADMIN_USERNAME)
        page.fill("#password", ADMIN_PASSWORD)
        page.click("#login-btn")

        # 登录成功后会自动跳到首页
        expect(page).to_have_url(BASE_URL + "/index.html")

        # storage_state 会把 localStorage 里的 token 一起保存下来
        context.storage_state(path=AUTH_STATE_FILE)
        browser.close()

    print("登录态已保存：" + AUTH_STATE_FILE)


if __name__ == "__main__":
    main()
