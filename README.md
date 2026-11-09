# ♻️ 循展 LoopExpo — 高校活动智能服务平台

**让每一场精彩，不止一次。**

本仓库是浙江师范大学《创新创业实训》课程商业计划书的教学演示原型，展示“AI 智能策划 + 循环物料共享 + 线下履约”的产品闭环。

## 在线功能

- ✨ 活动需求输入与活动策划建议：按活动类型、参与人数、时间、预算和设计风格推荐
- 📦 物料库存与预约日期约束：依据模拟库存实时匹配可执行套餐
- 💴 自动报价：基础展示 ¥199、标准活动 ¥399、综合活动 ¥899（**模拟价格**）
- 🚚 模拟订单：下单、审核、待履约、已完成与库存释放
- 🌱 循环利用看板：展示模拟库存、复用件次和活动完成数
- 🤖 可选 AI API：配置服务端密钥后，按确定性推荐结果生成活动主题与视觉建议

**所有库存、费用、订单、复用数据都是教学假设，不代表实际经营。** 当前订单仅保存在单个 Streamlit 会话内；不收款、不收集用户真实资料。

## 部署 Streamlit Community Cloud

1. 打开 https://share.streamlit.io ，登录并授权 GitHub。
2. 点击 **Create app** → **Deploy a public app from GitHub**（文字可能略有不同）。
3. Repository：`2499085224-lgtm/loopexpo-demo`
4. Branch：`main`
5. Main file path：`streamlit_app.py`
6. 如提示 Python 版本，选择受支持的默认版本即可；依赖在根目录的 `requirements.txt` 自动安装。
7. 点击 **Deploy**。部署成功后复制实际生成的 `https://<你的子域名>.streamlit.app` 网址并用手机访问确认。
8. 将已经验证的真实网址生成二维码，放到商业计划书的项目展示页。

## 接入 AI API（非必需）

应用在没有 API 的情况下也能完成规则匹配、报价、订单及看板演示。

如果需要生成真实 AI 策划文案，在 Streamlit Cloud 的 App Settings → Secrets 中配置：

```toml
AI_API_KEY = "你的真实密钥"
AI_MODEL = "兼容Chat Completions的模型ID"
AI_BASE_URL = "https://你的服务商API根地址/v1"
```

仅使用兼容 OpenAI Chat Completions 的服务端接口。切勿把真实密钥提交到 GitHub、放在二维码链接里或发到公开网页；`.streamlit/secrets.toml.example` 仅是空白示例。

## 本地启动

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 文件说明

- `streamlit_app.py` — 主程序
- `requirements.txt` — 部署依赖
- `.streamlit/secrets.toml.example` — 可选 AI 密钥示例（不含真实密钥）
- `.gitignore` — 防止误上传本地密钥和缓存

## 设计与安全边界

平台使用可解释的业务规则匹配库存和报价；AI 只负责可选文案生成，不能替代安全审核、正式报价或真实库存管理。本项目仅用于教学演示，不能作为真实采购、租赁或支付服务。

