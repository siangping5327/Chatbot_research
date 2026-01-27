from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 題目分數表（只做 Q1 + Q2）
# =========================
# 方法 1：按題目分層管理 TEXT_TO_VALUE
TEXT_TO_VALUE = {
    "Q２": {
        "少於 3 小時": "short",
        "3–6 小時": "medium",
        "6 小時以上": "long",
        "略過": "skip",
        "略過/不願透露": "skip",
    },
    "Q３": {
        "是": "true",
        "否，會低頭": "false",
        "略過": "skip"
    }
}

SCORE_MAP = {
    "Q２": {
        "short": 0,
        "medium": 1,
        "long": 2,
        "skip": 0
    },
    "Q３": {
        "true": 2,
        "false": 1,
        "skip": 0
    }
}

SCORABLE_INTENTS = {"Q２", "Q３"}


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    intent = req["queryResult"]["intent"]["displayName"]
    raw_text = req["queryResult"]["queryText"].strip()

    # =========================
    # 將使用者輸入映射成對應的值（按題目分層）
    # =========================
    mapped_value = TEXT_TO_VALUE.get(intent, {}).get(raw_text, raw_text.lower())

    print(f"[DEBUG] intent={intent}")
    print(f"[DEBUG] raw_text={raw_text}")
    print(f"[DEBUG] mapped_value={mapped_value}")

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
    if intent in SCORABLE_INTENTS:
        score_added = SCORE_MAP[intent].get(mapped_value, 0)
        state["score"] += score_added
        print(f"[DEBUG] add={score_added}, total={state['score']}")
    else:
        print(f"[DEBUG] intent {intent} not scorable")

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

   

