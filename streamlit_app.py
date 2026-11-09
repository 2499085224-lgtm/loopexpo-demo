"""循展 LoopExpo：AI 活动策划 + 循环物料租赁教学演示。所有库存及财务数据均为模拟。"""
import json
import os
from datetime import date, timedelta
import requests
import streamlit as st

st.set_page_config(page_title="循展 LoopExpo | 高校活动智能工作台", page_icon="♻️", layout="wide")
st.markdown("""<style>
.block-container{padding-top:2rem;max-width:1280px} h1,h2,h3{color:#125a40!important}
div[data-testid="stMetric"]{border:1px solid #d6e7db;border-radius:14px;padding:14px;background:#f5faf7}
.stButton>button[kind="primary"]{background:#156d4d;border:none;border-radius:9px}
</style>""", unsafe_allow_html=True)

INVENTORY = {
    "模块化背景框架": {"qty": 12, "cost": 350, "reuse": 8},
    "可复用展架": {"qty": 35, "cost": 90, "reuse": 13},
    "导视牌支架": {"qty": 28, "cost": 60, "reuse": 11},
    "模块化签到台": {"qty": 8, "cost": 240, "reuse": 6},
    "低功耗补光灯": {"qty": 14, "cost": 180, "reuse": 7},
    "展示板组件": {"qty": 50, "cost": 55, "reuse": 15},
}
PACKAGES = {
    "基础展示": {"price": 199, "variable_cost": 95, "people": 45, "items": {"可复用展架": 2, "导视牌支架": 2, "展示板组件": 1}},
    "标准活动": {"price": 399, "variable_cost": 213, "people": 125, "items": {"模块化背景框架": 1, "可复用展架": 2, "导视牌支架": 2}},
    "综合活动": {"price": 899, "variable_cost": 510, "people": 500, "items": {"模块化背景框架": 2, "可复用展架": 4, "导视牌支架": 4, "模块化签到台": 1, "低功耗补光灯": 2}},
}
if "orders" not in st.session_state:
    st.session_state.orders = []
if "proposal" not in st.session_state:
    st.session_state.proposal = None

def available(item, day):
    blocked = sum(o["items"].get(item, 0) for o in st.session_state.orders
                  if o["date"] == day and o["status"] in ("待审核", "待履约"))
    return INVENTORY[item]["qty"] - blocked

def recommend(budget, people, day):
    options = []
    for name, config in PACKAGES.items():
        if budget < config["price"] or people > config["people"]:
            continue
        if all(available(item, day) >= amount for item, amount in config["items"].items()):
            options.append((config["price"], name))
    return max(options)[1] if options else None

def ai_settings(name, default=""):
    try:
        return st.secrets.get(name, os.environ.get(name, default))
    except (FileNotFoundError, KeyError):
        return os.environ.get(name, default)

def generate_ai_copy(event, category, style, budget, package):
    key = ai_settings("AI_API_KEY")
    model = ai_settings("AI_MODEL")
    base = ai_settings("AI_BASE_URL", "https://api.openai.com/v1")
    if not key or not model:
        return "AI 尚未配置，已使用可解释的库存匹配算法生成方案。请在应用后台 Secrets 中配置 API。"
    endpoint = base.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint += "/chat/completions"
    try:
        result = requests.post(
            endpoint,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"model": model, "messages": [
                {"role": "system", "content": "你是高校活动策划助手。请用中文回答，不得保证实际库存或未经核实的环保减排成果。"},
                {"role": "user", "content": f"为{event[:70]}设计活动视觉概念及执行要点。活动类型：{category}，风格：{style}，预算：{budget}元，实际规则引擎建议：{package}。输出活动主题、视觉创意、执行提示三段，260字以内。"}
            ], "temperature": 0.65, "max_tokens": 500},
            timeout=25)
        result.raise_for_status()
        return str(result.json()["choices"][0]["message"]["content"])[:1500]
    except Exception as err:
        return f"AI 接口暂不可用（{type(err).__name__}）。库存与报价结果仍有效，请核实服务商的模型、接口与额度。"

st.title("♻️ 循展 LoopExpo")
st.caption("让每一场精彩，不止一次。 | AI 智能策划 × 校园循环物料共享 × 线下活动履约")
st.info("课程项目 Demo：库存、采购价、历史复用、订单及财务均为教学模拟数据；不接受真实订单或付款。")

tab1, tab2, tab3, tab4 = st.tabs(["✨ AI 活动策划", "📦 物料库存", "🚚 订单履约", "🌱 循环看板"])
with tab1:
    c1, c2 = st.columns([1, 1.1], gap="large")
    with c1:
        st.subheader("01 录入活动需求")
        event = st.text_input("活动名称", "大学生创新成果展", max_chars=70)
        category = st.selectbox("活动类型", ["学院成果展", "社团招新", "讲座论坛", "科创比赛", "毕业季展示", "其他"])
        a, b = st.columns(2)
        with a:
            people = st.number_input("预计参与人数", 10, 500, 80, step=10)
        with b:
            budget = st.number_input("物料预算（元）", 100, 100000, 650, step=50)
        day = str(st.date_input("活动日期", date.today() + timedelta(days=14)))
        style = st.selectbox("主视觉风格", ["科技绿", "学术蓝", "青春橙", "简约黑白"])
        notes = st.text_area("补充需求", "需要签到台、背景板和导视区域，支持当天拆装。", max_chars=400)
        use_ai = st.toggle("启用在线 AI 策划文案（需要服务器端 API 密钥）")
        clicked = st.button("生成可执行活动方案", type="primary", use_container_width=True)
        if clicked:
            choice = recommend(int(budget), int(people), day)
            if choice is None:
                st.session_state.proposal = None
                st.error("预算、参与人数或所选日期库存不满足现有套餐要求。请调整条件或申请定制报价。")
            else:
                p = PACKAGES[choice]
                desc = generate_ai_copy(event, category, style, budget, choice) if use_ai else (
                    f"建议采用「{style}」模块化视觉系统，突出活动主题并复用框架、导视组件。"
                    "活动当天按场地核定安装尺寸；宣传文案、结构安全、出入许可均需人工复核。")
                st.session_state.proposal = {
                    "event": event, "category": category, "people": int(people), "budget": int(budget),
                    "date": day, "style": style, "notes": notes, "package": choice,
                    "price": p["price"], "variable_cost": p["variable_cost"],
                    "items": p["items"], "description": desc
                }
    with c2:
        st.subheader("02 方案与报价")
        proposal = st.session_state.proposal
        if proposal is None:
            st.write("先输入左侧需求，再点击「生成可执行活动方案」。")
            st.caption("推荐逻辑会验证套餐价格、人数上限及当前会话的日期级库存。")
        else:
            st.success("推荐 " + proposal["package"] + "套餐 · 预算与模拟库存满足")
            x, y, z = st.columns(3)
            x.metric("套餐报价", "¥" + str(proposal["price"]))
            y.metric("预算余额", "¥" + str(proposal["budget"] - proposal["price"]))
            z.metric("贡献毛利（模拟）", "¥" + str(proposal["price"] - proposal["variable_cost"]))
            st.progress(min(1.0, proposal["price"] / max(proposal["budget"], 1)),
                        text="预算使用比例")
            st.markdown("**活动策划建议**")
            st.write(proposal["description"])
            st.markdown("**物料清单及可用量**")
            st.dataframe([{"物料": n, "预订数量": q, "当前可用": available(n, proposal["date"])}
                          for n, q in proposal["items"].items()],
                         hide_index=True, use_container_width=True)
            l, r = st.columns(2)
            with l:
                st.download_button("下载方案 JSON", json.dumps(proposal, ensure_ascii=False, indent=2),
                                   "LoopExpo_proposal.json", "application/json", use_container_width=True)
            with r:
                if st.button("提交模拟订单", type="primary", use_container_width=True):
                    if recommend(proposal["budget"], proposal["people"], proposal["date"]) != proposal["package"]:
                        st.error("库存发生变化，请重新生成方案。")
                    elif any(available(k, proposal["date"]) < q for k, q in proposal["items"].items()):
                        st.error("库存不足，请重新生成方案。")
                    else:
                        order = dict(proposal)
                        order.update({"id": f"LX{len(st.session_state.orders)+1:04d}", "status": "待审核"})
                        st.session_state.orders.append(order)
                        st.success(f"已创建模拟订单 {order['id']}，请前往「订单履约」查看。")

with tab2:
    st.subheader("循环物料库存台账")
    st.caption("演示数据，不是实际仓库。待审核、待履约的同日订单会占用对应库存。")
    st.dataframe([{"名称": n, "总库存": v["qty"], "示例采购单价": v["cost"],
                   "历史模拟复用次数/件": v["reuse"], "今日可用": available(n, str(date.today()))}
                  for n, v in INVENTORY.items()], hide_index=True, use_container_width=True)
    st.write("库存分配采用硬约束，而非让 AI 虚构库存、价格或交货能力。")

with tab3:
    st.subheader("订单履约工作台")
    if not st.session_state.orders:
        st.info("尚无模拟订单。请先到「AI 活动策划」选项卡提交订单。")
    for i, order in enumerate(st.session_state.orders):
        with st.container(border=True):
            left, right = st.columns([3, 1])
            left.markdown(f"**{order['id']} | {order['event']}**")
            left.caption(f"{order['date']} · {order['package']} · ¥{order['price']} · {order['status']}")
            if order["status"] == "待审核":
                if right.button("审核通过", key=f"approve{i}", use_container_width=True):
                    order["status"] = "待履约"
                    st.rerun()
            elif order["status"] == "待履约":
                if right.button("完成并回收", key=f"done{i}", use_container_width=True):
                    order["status"] = "已完成"
                    st.rerun()
            else:
                right.success("已完成")
    if st.session_state.orders and st.button("清空本会话模拟订单"):
        st.session_state.orders = []
        st.session_state.proposal = None
        st.rerun()

with tab4:
    st.subheader("物料循环使用概览")
    completed = [o for o in st.session_state.orders if o["status"] == "已完成"]
    initial_reuses = sum(v["qty"] * v["reuse"] for v in INVENTORY.values())
    new_reuses = sum(sum(o["items"].values()) for o in completed)
    a, b, c = st.columns(3)
    a.metric("模拟总资产", f"{sum(v['qty'] for v in INVENTORY.values())} 件")
    b.metric("累计复用件次（模拟）", initial_reuses + new_reuses)
    c.metric("本会话完成订单", len(completed))
    st.bar_chart({name: v["qty"] for name, v in INVENTORY.items()}, horizontal=True)
    st.caption("不直接将复用件次等同于碳减排量；真实环境效益需考虑替代率、运输和维护等边界。")

st.divider()
st.caption("浙江师范大学《创新创业实训》课程项目演示 | 2026 年 11 月。请勿提交真实个人信息。")
