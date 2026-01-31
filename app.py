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
    "否，會低頭": 2
}

# =========================
# 2️⃣ Webhook 主程式
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)

    intent_name = req["queryResult"]["intent"]["displayName"]
    user_text = req["queryResult"].get("queryText", "")
    session_params = req["queryResult"].get("parameters", {})

    # ---- 目前累積分數（沒有就從 0 開始）----
    current_score = session_params.get("total_score", 0)

    print("Intent:", intent_name)
    print("User text:", user_text)
    print("Current score:", current_score)

    # =========================
    # Ending：只顯示總分
    # =========================
    if intent_name == "Ending":
        return jsonify({
            "fulfillmentText": f"風險分數為 {current_score} 分"
        })

    # =========================
    # 其他題目：只加分，不顯示文字
    # =========================
    add_score = SCORE_MAP.get(user_text, 0)
    new_score = current_score + add_score
    session_params["total_score"] = new_score

    print("Add score:", add_score)
    print("New total score:", new_score)

    return jsonify({
        "fulfillmentText": "",
        "parameters": session_params
    })


# =========================
# 3️⃣ Render 啟動
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)










