from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 1️⃣ 選項文字 → 分數
# =========================
SCORE_MAP = {
    # Q1
    "少於 3 小時": 0,
    "3–6 小時": 1,
    "6 小時以上": 2,

    # Q2
    "是": 1,
    "否，會低頭": 2,
}

# 👉 只有「最終顯示」的 intent
ENDING_INTENTS = [
    "Ending"
]

# =========================
# 2️⃣ Webhook 主程式
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)

    intent_name = req["queryResult"]["intent"]["displayName"]
    user_text = req["queryResult"].get("queryText", "")
    session = req.get("session", "")

    # =========================
    # 🔍 找 score_context
    # =========================
    output_contexts = req["queryResult"].get("outputContexts", [])
    score_context = None

    for c in output_contexts:
        if c["name"].endswith("/contexts/score_context"):
            score_context = c
            break

    # =========================
    # 🧮 讀取目前累積分數（超級防呆）
    # =========================
    raw_score = 0
    if score_context:
        raw_score = score_context.get("parameters", {}).get("total_score", 0)

    try:
        current_score = float(raw_score)
    except (ValueError, TypeError):
        current_score = 0.0

    print("Intent:", intent_name)
    print("User text:", user_text)
    print("Current score:", current_score)

    # =========================
    # 🛑 Ending：只顯示，不動分數、不回 context
    # =========================
    if intent_name in ENDING_INTENTS:
        return jsonify({
            "fulfillmentText": f"風險分數為 {current_score} 分"
        })

    # =========================
    # ➕ 其他 intent（包含 Ending1）：加分
    # =========================
    add_score = SCORE_MAP.get(user_text, 0)

    try:
        add_score = int(add_score)
    except (ValueError, TypeError):
        add_score = 0

    new_total_score = current_score + add_score

    print("Add score:", add_score)
    print("New total score:", new_total_score)

    # =========================
    # 🔁 回傳更新後的 score_context
    # =========================
    return jsonify({
        "fulfillmentText": "",
        "outputContexts": [
            {
                "name": f"{session}/contexts/score_context",
                "lifespanCount": 50,
                "parameters": {
                    "total_score": new_total_score
                }
            }
        ]
    })

# =========================
# 3️⃣ Render / Local 啟動
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
