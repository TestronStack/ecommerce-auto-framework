import os

# 被测服务地址
BASE_URL = "http://localhost:8089"
API_URL = BASE_URL + "/api"

# 管理员账号（应用启动时 DataInitializer 自动创建）
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123456"

# 目录路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
REPORT_DIR = os.path.join(ROOT_DIR, "reports")

# Playwright 登录态文件（登录一次，全局复用）
AUTH_STATE_FILE = os.path.join(ROOT_DIR, "tests", "auth_state.json")
