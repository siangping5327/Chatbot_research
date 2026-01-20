from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 風險分數對照表（核心）
# =========================
SCORE_MAP = {
    "Q2": {   # 螢幕時間
        "long": 2,
        "medium": 1,
        "short": 0,
        "skip": 0
    },
    "Q3": {   # 姿勢／行為題
        "true": 2,
        "false": 1,
        "skip": 0
    }
}

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    # 取得 intent 名稱
    intent = req["queryResult"]["intent"]["displayName"]

    # 取得參數
    params = req["queryResult"].get("parameters", {})
    answer = params.get("answer")

    # === MVP：用 session 當 state（不做長期儲存）===
    # Dialogflow ES session 是暫時的
    output_contexts = req["queryResult"].get("outputContexts", [])

    state = {"score": 0}

    for ctx in output_contexts:
        if "session-vars" in ctx["name"]:
            state = ctx.get("parameters", state)

    # =========================
    # 根據對照表累加分數
    # =========================
    if intent in SCORE_MAP and answer:
        state["score"] += SCORE_MAP[intent].get(answer, 0)

    # =========================
    # 最後一題 Ending
    # =========================
    if intent == "Ending":
        total_score = state["score"]
        if total_score <= 2:
            level = "低"
        elif total_score <= 4:
            level = "中"
        else:
            level = "高"

        response_text = f"🎯 你的科技頸風險總分為 {total_score} 分（{level} 風險）"

        # 用完可以清掉 session state（選擇性）
        return jsonify({
            "fulfillmentText": response_text
        })

    # =========================
    # 回傳結果（MVP 版）
    # =========================
    response_text = f"目前累積的科技頸風險分數為 {state['score']} 分（僅供參考）"

    return jsonify({
        "fulfillmentText": response_text,
        "outputContexts": [
            {
                "name": f"{req['session']}/contexts/session-vars",
                "lifespanCount": 10,
                "parameters": state
            }
        ]
    })"Webhook 成功連線！🚀"})











