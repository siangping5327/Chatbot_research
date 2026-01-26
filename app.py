from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 分數對照表（SCORE_MAP）
# =========================
SCORE_MAP = {
    "Q1": {"short": 0, "medium": 1, "long": 2, "skip": 0},
    "Q2": {"true": 2, "false": 1, "skip": 0}
}

# =========================
# 文字 → value 映射表（對應 richContent）
# =========================
TEXT_TO_VALUE_MAP = {
    "Q1": {
        "少於 3 小時": "short",
        "3–6 小時": "medium",
        "6 小時以上": "long",
        "略過／不願透露": "skip"
    },
    "Q2": {
        "是": "true",
        "否，會低頭": "false",
        "略過／不願透露": "skip"
    }
}

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    intent = req["queryResult"]["intent"]["displayName"]

    # =========================
    # 讀取使用者實際看到的文字（chips text）
    # =========================
    raw_text = req["queryResult"].get("queryText", "").strip()

    # 根據 intent 做「文字 → value」轉換
    answer = TEXT_TO_VALUE_MAP.get(intent, {}).get(raw_text)

    # Debug
    print(f"[DEBUG] intent={intent}")
    print(f"[DEBUG] raw_text={raw_text}")
    print(f"[DEBUG] mapped_answer={answer}")

    # =========================
    # 讀取 score-session context
    # =========================
    output_contexts = req["queryResult"].get("outputContexts", [])
    state = {"score": 0}
    for ctx in output_contexts:
        if ctx["name"].endswith("/contexts/score-session"):
            state = ctx.get("parameters", {"score": 0})
            state.setdefault("score", 0)

    # =========================
    # 累加分數
    # =========================
    if intent in SCORE_MAP and answer:
        state["score"] += SCORE_MAP[intent].get(answer, 0)

    print(f"[DEBUG] score={state['score']}")

    # =========================
    # Ending intent
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
            "fulfillmentText": f"您的科技頸風險總分為 {total_score} 分（{level} 風險）",
            "outputContexts": [
                {
                    "name": f"{req['session']}/contexts/score-session",
                    "lifespanCount": 0,
                    "parameters": state
                }
            ]
        })

    # =========================
    # 回存 score-session
    # =========================
    return jsonify({
        "outputContexts": [
            {
                "name": f"{req['session']}/contexts/score-session",
                "lifespanCount": 100,
                "parameters": state
            }
        ]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)























