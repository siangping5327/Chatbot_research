from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 風險分數對照表（測試版：Q2 + Q3）
# =========================
SCORE_MAP = {
    "Q2": {   # 第一題（示例）
        "long": 2,
        "medium": 1,
        "short": 0,
        "skip": 0
    },
    "Q3": {   # 第二題（示例）
        "true": 2,
        "false": 1,
        "skip": 0
    }
}

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    intent = req["queryResult"]["intent"]["displayName"]

    # =========================
    # 嘗試從 parameters 讀取 answer；若沒有，就用 queryText
    # =========================
    params = req["queryResult"].get("parameters", {})
    answer = params.get("answer")

    if not answer:
        # Dialogflow ES 點選 chips 後，使用 queryText
        answer = req["queryResult"].get("queryText", "").strip().lower()
    
    # =========================
    # 讀取 score-session，確保 state["score"] 存在
    # =========================
    output_contexts = req["queryResult"].get("outputContexts", [])
    state = {"score": 0}

    for ctx in output_contexts:
        if ctx["name"].endswith("/contexts/score-session"):
            state = ctx.get("parameters", {})
            if "score" not in state:
                state["score"] = 0

    # =========================
    # 累加分數（只對 SCORE_MAP 中的題目）
    # =========================
    if intent in SCORE_MAP and answer:
        key = answer.lower()
        state["score"] += SCORE_MAP[intent].get(key, 0)
    
    # Debug：確認有沒有成功加分
    print(f"[DEBUG] intent={intent}, answer={answer}, score={state['score']}")

    # =========================
    # Ending intent：顯示結果
    # =========================
    if intent == "Ending":
        total_score = state["score"]

        if total_score <= 2:
            level = "低"
        elif total_score <= 4:
            level = "中"
        else:
            level = "高"

        return jsonify({
            "fulfillmentText": f" 您的科技頸風險總分為 {total_score} 分（{level}風險）"
        })

    # =========================
    # 中間題目：只回傳 context（不影響 payload）
    # =========================
    return jsonify({
        "outputContexts": [
            {
                "name": f"{req['session']}/contexts/score-session",
                "lifespanCount": 1,
                "parameters": state
            }
        ]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


















