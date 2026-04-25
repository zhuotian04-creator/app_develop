# School Market

一个基于 `uni-app + Django` 的校园二手交易 / 租赁小程序原型项目。

这个项目是我用于练手和作品展示的第一个完整仓库，包含小程序前端、Django 后端、商品发布、消息沟通、个人中心，以及一个“语音描述后自动填表”的智能发布流程。

## 项目亮点

- 校园二手交易与租赁双模式
- 小程序首页商品流、详情页、消息页、个人中心
- 发布页支持语音识别后自动提取标题、分类、成色、使用时长、价格等信息
- Django REST API 提供商品、消息、个人信息、图片上传等接口
- 支持本地规则提取，未配置 AI Key 也可以体验自动填表流程

## 技术栈

- 前端：`uni-app`、Vue
- 后端：`Django`、`Django REST Framework`
- 运行环境：微信开发者工具、HBuilderX

## 项目结构

```text
school-market/
├── api/                        # 前端接口封装
├── components/                 # 通用组件
├── pages/secondhand/           # 小程序业务页面
├── static/                     # 静态资源
├── secondhand_backend/         # Django 后端
├── App.vue
├── main.js
├── pages.json
└── manifest.json
```

## 主要页面

- `pages/secondhand/index/index`：首页商品列表
- `pages/secondhand/detail/detail`：商品详情
- `pages/secondhand/publish/publish`：智能发布页
- `pages/secondhand/message/message`：消息列表
- `pages/secondhand/chat/chat`：聊天页
- `pages/secondhand/my/my`：个人中心

## 本地运行

### 1. 启动 Django 后端

进入后端目录：

```powershell
cd C:\Users\28566\Documents\HBuilderProjects\school-market\secondhand_backend
```

安装依赖：

```powershell
pip install -r requirements.txt
```

执行迁移：

```powershell
python manage.py migrate
```

启动服务：

```powershell
python manage.py runserver 0.0.0.0:8000
```

后台管理地址：

- `http://127.0.0.1:8000/admin/`

接口示例：

- `http://127.0.0.1:8000/api/secondhand/products/`

### 2. 启动小程序前端

1. 用 `HBuilderX` 打开项目根目录
2. 运行到微信开发者工具
3. 确保 `api/secondhand.js` 中的 `BASE_URL` 指向你当前电脑的局域网地址

## 关于语音智能发布

发布页支持两种方式：

- 按住说话：录音结束后自动识别并填充表单
- 手动输入：直接输入描述，再点击“重新识别并自动填写”

当前会尽量提取：

- 商品标题
- 分类
- 成色
- 使用时长（月）
- 价格
- 商品描述

如果未配置真实 AI Key，后端会使用本地规则做基础提取，方便演示和开发。

## 后续优化方向

- 接入真实语音转文本与大模型提取能力
- 接入对象存储，替换演示图片资源
- 优化微信小程序环境下的图片资源加载
- 增加收藏、订单、支付等完整交易流程

## 说明

这是一个原型项目，当前更偏向功能验证和作品展示。
