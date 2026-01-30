from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 題目分數表（只做 Q1 + Q2 作為範例，可延伸）
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
    
    print(f"[DEBUG] intent={intent}")
    print(f"[DEBUG] full request body: {req}")

    # =========================
    # 直接從 parameters 讀取各題答案
    # =========================
    params = req["queryResult"].get("parameters", {})
    total_score = 0

    for q, mapping in SCORE_MAP.items():
        ans = params.get(q.lower(), "skip")  # 注意參數名稱要和 Dialogflow 裡的名稱對應
        total_score += mapping.get(ans, 0)
        print(f"[DEBUG] {q} answer={ans}, current total={total_score}")

    # =========================
    # Ending Intent 回傳總分
    # =========================
    if intent == "Ending":
        return jsonify({
            "fulfillmentText": f" 您的科技頸風險總分為 {total_score} 分"
        })

    # =========================
    # 非 Ending Intent 回傳空訊息即可
    # =========================
    return jsonify({
        "fulfillmentText": f"已記錄您的回答：{params}"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)






