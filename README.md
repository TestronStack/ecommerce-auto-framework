# 电商平台自动化测试框架

![Python](https://img.shields.io/badge/Python-3.11-blue)
![pytest](https://img.shields.io/badge/pytest-9.2-brightgreen)
![Playwright](https://img.shields.io/badge/Playwright-1.5x-2EAD33)
![Allure](https://img.shields.io/badge/Allure-2.27-orange)
![Tests](https://img.shields.io/badge/tests-124%20(117%20passed)-success)
![Report](https://img.shields.io/badge/Allure%20Report-GitHub%20Pages-blueviolet)

一套针对 Spring Boot 电商系统的 **接口自动化 + UI 自动化** 测试框架，用 Python 从 0 搭建，覆盖 52 个 REST 接口、6 大业务模块，共 124 条用例。

> 报告在线预览：https://testronstack.github.io/ecommerce-auto-framework/

---

## 项目背景

被测系统是一个电商平台（用户 / 商品 / 分类 / 购物车 / 订单 / 评价 6 个模块，52 个接口），后端 Spring Boot 3 + Spring Security + JWT + JPA + MySQL。

两个特点决定了用例怎么写：

- **HTTP 状态码恒为 200**，真实结果在响应体的 `code` 字段（200 成功 / 400 参数错误 / 401 未登录 / 403 无权限 / 404 不存在 / 500 服务端异常）
- **资源删除需要 ADMIN 角色**，普通用户调用删除接口返回 403

所以断言不能只看 `status_code`，必须校验业务码、提示消息和数据内容。

本仓库只包含测试代码，被测系统为个人学习项目。

---

## 技术栈

| 分类 | 技术 |
|---|---|
| 语言 | Python 3.11 |
| 测试框架 | pytest 9.2 |
| 接口请求 | requests |
| UI 自动化 | Playwright（pytest-playwright） |
| 测试报告 | allure-pytest + Allure Commandline |
| 数据驱动 | JSON |

---

## 目录结构

```
ecommerce-auto-framework/
├── api/                     # 接口对象层：一个模块一个类，一个方法对应一个接口
│   ├── base_api.py          # 基类：Session、公共 Header、Token 注入、get/post/put/delete
│   ├── user_api.py          # 用户模块 8 个接口
│   ├── product_api.py       # 商品模块 11 个接口
│   ├── category_api.py      # 分类模块 8 个接口
│   ├── cart_api.py          # 购物车模块 6 个接口
│   ├── order_api.py         # 订单模块 10 个接口
│   └── review_api.py        # 评价模块 9 个接口
├── config/
│   └── settings.py          # 被测地址、管理员账号、目录路径、登录态文件路径
├── data/                    # 测试数据（数据与代码分离）
│   ├── user_data.json       # 用户局部更新场景
│   └── order_data.json      # 收货信息
├── pages/                   # 页面对象层：一个页面一个类，只放元素定位和页面操作
│   ├── login_page.py
│   ├── index_page.py
│   ├── cart_page.py
│   ├── checkout_page.py
│   └── orders_page.py
├── tests/                   # 用例层
│   ├── conftest.py          # fixture：全局登录、临时数据、权限参数化、UI 登录态
│   ├── create_auth_state.py # 工具脚本：生成 Playwright storage_state
│   ├── test_check_login.py  # 登录 7 条
│   ├── test_user.py         # 用户 12 条
│   ├── test_product.py      # 商品 12 条
│   ├── test_category.py     # 分类 9 条
│   ├── test_cart.py         # 购物车 7 条
│   ├── test_order.py        # 订单 10 条
│   ├── test_review.py       # 评价 10 条
│   ├── test_boundary.py     # 边界值 / 异常场景 55 条
│   ├── test_full_flow.py    # 17 步全链路 1 条
│   └── test_ui_shop_flow.py # UI 主链路 1 条
├── docs/                    # Allure 报告静态站点（供 GitHub Pages 部署）
├── reports/                 # 本地运行产物（已 gitignore）
├── pytest.ini
└── requirements.txt
```

---

## 环境要求

- Python 3.11+
- 被测应用已启动，默认地址 `http://localhost:8089`
- Allure Commandline（仅生成 HTML 报告时需要）

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 确认被测应用可访问（默认 http://localhost:8089）
curl http://localhost:8089/api/user

# 3. 生成 UI 登录态（UI 用例依赖，只需执行一次，Token 24 小时有效）
python tests/create_auth_state.py

# 4. 跑全量用例
pytest

# 5. 生成并查看 Allure 报告
allure generate reports/tmp -o reports/html --clean
allure open reports/html
```

只跑接口用例（跳过 UI）：

```bash
pytest --ignore=tests/test_ui_shop_flow.py
```

---

## 用例覆盖

| 测试文件 | 条数 | 覆盖内容 |
|---|---|---|
| test_check_login.py | 7 | 管理员登录、密码错误、用户不存在、随机注册、重名、密码长度、无 Token |
| test_user.py | 12 | 全量 / 分页 / 按 ID / 按用户名查询、404、JSON 数据驱动的局部更新、删除权限矩阵 |
| test_product.py | 12 | 增删改查、分页、按分类 / 状态 / 关键词 / 价格区间查询、图片上传 |
| test_category.py | 9 | 增删改查、分页、重名、不存在 |
| test_cart.py | 7 | 加购、查询、改数量、删除、重复加购合并、清空 |
| test_order.py | 10 | 购物车下单、直接下单、列表、详情、支付、发货、收货、取消、删除 |
| test_review.py | 10 | 评价增删改查、按商品查、按用户查、评分边界 |
| test_boundary.py | 55 | 用户名 3/4/20/21 位、密码 5/6 位、邮箱非法格式、价格 -1/0、库存 -1/0、商品名 1/2/100/101 字、数量 0/-1、超库存、空购物车、状态非法值、分页 size=0/1000、page=-1、路径参数传 abc 等 |
| test_full_flow.py | 1 | 注册→登录→建分类→建商品→加购→下单→支付→收货→评价 全链路 17 步 |
| test_ui_shop_flow.py | 1 | 首页加购→购物车角标→结算→填收货信息→提交订单→支付跳转 |
| **合计** | **124** | **117 passed + 7 xfailed** |

### 框架设计要点

- **分层**：`tests` 只写业务和断言，URL 藏在 `api`，定位器藏在 `pages`，地址藏在 `config`，数据藏在 `data`
- **登录一次**：`admin_token` 是 session 级 fixture，全流程只登录一次
- **数据不写死**：用户名 / 邮箱用「时间戳 + 随机数」生成，用例可重复执行
- **权限参数化**：`indirect` 参数化 `["admin", "user"]`，2 条用例覆盖两种角色 × 一个接口
- **UI 复用登录态**：Playwright `storage_state` 保存 localStorage 中的 Token，避免每条 UI 用例重复登录
- **动态断言**：业务码 + 提示消息 + 数据字段三层校验

---

## 已发现缺陷（7 条，已写成 `xfail(strict=True)`）

这些都是实际跑出来的，不是猜测。修复后用例会从 xfail 变成 xpass 并报错，自动提醒回归。

| # | 场景 | 实际结果 | 期望结果 | 原因 |
|---|---|---|---|---|
| 1 | 商品描述传 500 字 | 500 | 200 | 实体 `@Size(max=500)` 通过，但数据库 `description` 列长度不足，报 `Data too long` |
| 2 | 加购不存在的商品 | 500 | 404 | 外键约束异常未被业务层处理 |
| 3 | 直接下单不存在的商品 | 500 | 404 | 同上 |
| 4 | 订单状态传 `ABC` | 200 更新成功 | 400 | 状态字段无枚举校验，脏数据可入库 |
| 5 | 支付状态传 `ABC` | 200 更新成功 | 400 | 同上 |
| 6 | 改状态不传 `status` 参数 | 500 | 400 | 缺少必填参数校验 |
| 7 | 分页排序字段传 `abc` | 500 | 400 | 直接拼进 Spring Data 排序，抛 `No property 'abc' found` |

---

## 测试报告

Allure 报告包含每个用例的步骤、请求 / 响应、失败截图与 trace。

- 在线预览：https://testronstack.github.io/ecommerce-auto-framework/
- 本地生成：`pytest` 后执行 `allure generate reports/tmp -o reports/html --clean`

---

## 说明

- `tests/auth_state.json` 内含登录 Token，已加入 `.gitignore`，不会提交
- `reports/` 为每次运行重新生成的产物，不纳入版本库
- `config/settings.py` 中的 `admin/123456` 是被测应用初始化时自动创建的默认管理员账号
