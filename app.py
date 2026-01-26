from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 題目分數表（只做 Q1 + Q2）
# =========================
SCORE_MAP = {
    "Q1": {
        "short": 0,
        "medium": 1,
        "long": 2,
        "skip": 0
    },
    "Q2": {
        "true": 2,
        "false": 1,
        "skip": 0
    }
}

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    intent = req["queryResult"]["intent"]["displayName"]
    raw_text = req["queryResult"]["queryText"].strip().lower()

    print(f"[DEBUG] intent={intent}")
    print(f"[DEBUG] raw_text={raw_text}")

    # =========================
    # 讀取或初始化 score-session
    # =========================
    state = {"score": 0}
    for ctx in req["queryResult"].get("outputContexts", []):
        if ctx["name"].endswith("/contexts/score-session"):
            state = ctx.get("parameters", {"score": 0})
            state.setdefault("score", 0)

    # =========================
    # 累加分數（關鍵段落）
    # =========================
    if intent in SCORE_MAP:
        score_added = SCORE_MAP[intent].get(raw_text, 0)
        state["score"] += score_added
        print(f"[DEBUG] add={score_added}, total={state['score']}")

    # =========================
    # Ending：顯示總分
    # =========================
    if intent == "Ending":
        total = state["score"]
        return jsonify({
            "fulfillmentText": f"🎯 您的科技頸風險總分為 {total} 分",
            "outputContexts": [
                {
                    "name": f"{req['session']}/contexts/score-session",
                    "lifespanCount": 0,
                    "parameters": {}
                }
            ]
        })

    # =========================
    # 其他題目：回存 context
    # =========================
    return jsonify({
        "outputContexts": [
            {
                "name": f"{req['session']}/contexts/score-session",
                "lifespanCount": 50,
                "parameters": state
            }
        ]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

























