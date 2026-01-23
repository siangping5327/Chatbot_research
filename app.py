from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 分數對照表（SCORE_MAP）
# =========================
SCORE_MAP = {
    "Q2": {"long": 2, "medium": 1, "short": 0, "skip": 0},
    "Q3": {"true": 2, "false": 1, "skip": 0}
}

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    intent = req["queryResult"]["intent"]["displayName"]

    # =========================
    # 嘗試讀取使用者的 answer
    # =========================
    params = req["queryResult"].get("parameters", {})
    answer = params.get("answer") or req["queryResult"].get("queryText", "").strip().lower()

    # =========================
    # 讀取 score-session context（若不存在則初始化）
    # =========================
    output_contexts = req["queryResult"].get("outputContexts", [])
    state = {"score": 0}
    for ctx in output_contexts:
        if ctx["name"].endswith("/contexts/score-session"):
            state = ctx.get("parameters", {"score": 0})
            if "score" not in state:
                state["score"] = 0


    # =========================
    # 【核心段落】根據使用者選項計算分數，並累加到 state["score"]
    # =========================
    if intent in SCORE_MAP and answer:
        state["score"] += SCORE_MAP[intent].get(answer.lower(), 0)


    # Debug：印出目前分數
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

        # 回傳總分並清除 score-session context
        return jsonify({
            "fulfillmentText": f" 您的科技頸風險總分為 {total_score} 分（{level} 風險）",
            "outputContexts": [
                {
                    "name": f"{req['session']}/contexts/score-session",
                    "lifespanCount": 0,  # 清除 context
                    "parameters": state
                }
            ]
        })

    # =========================
    # 【核心段落】回存 score-session context，用於累計下一題
    # =========================
    return jsonify({
        "outputContexts": [
            {
                "name": f"{req['session']}/contexts/score-session",
                "lifespanCount": 100,  # 確保 context 不會過早消失
                "parameters": state
            }
        ]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)




















