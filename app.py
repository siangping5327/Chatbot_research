from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 1️⃣ 設定「選項文字 → 分數」
# 只放你「真的要計分的選項」
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

    # ---- 使用者剛剛選的文字 ----
    user_text = req["queryResult"].get("queryText", "")

    # ---- Session parameters（用來存總分）----
    session_params = req["queryResult"].get("parameters", {})

    # ---- 目前累積分數 ----
    current_score = session_params.get("total_score", 0)

    # ---- 本題加多少分 ----
    add_score = SCORE_MAP.get(user_text, 0)

    # ---- 更新總分 ----
    new_score = current_score + add_score
    session_params["total_score"] = new_score

    # ---- Debug 用（Render log 會看到）----
    print("User text:", user_text)
    print("Add score:", add_score)
    print("Total score:", new_score)

    # ---- 回傳給 Dialogflow ----
    return jsonify({
        "fulfillmentText": "",  # 文字交給 Dialogflow 本身處理
        "outputContexts": [
            {
                "name": req["queryResult"]["outputContexts"][0]["name"],
                "lifespanCount": 50,
                "parameters": session_params
            }
        ]
    })


# =========================
# 3️⃣ Render 需要的啟動方式
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)







