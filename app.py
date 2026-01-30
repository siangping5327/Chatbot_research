from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 題目分數表（只做 Q1 + Q2 作為範例，可延伸）
# 注意：這裡的 key "Q1", "Q2" 是 **對應你的 webhook 要抓的參數名稱**
# 如果你 Dialogflow 裡的 parameter 名稱不是 q1、q2，就要改這裡
# =========================
SCORE_MAP = {
    "q1_answer": {      # <-- 如果你的 Dialogflow parameter 叫 q1_answer，可以改成 "q1_answer"
        "short": 0,
        "medium": 1,
        "long": 2,
        "skip": 0
    },
    "q2_answer": {      # <-- 如果你的 Dialogflow parameter 叫 q2_answer，可以改成 "q2_answer"
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
    # 注意：下面這行會抓參數
    # params = req["queryResult"]["parameters"]
    # 這裡的 key 要跟你 Dialogflow Intent 裡的 parameter 名稱一致
    # =========================
    params = req["queryResult"].get("parameters", {})
    total_score = 0

    for q, mapping in SCORE_MAP.items():
        # 這裡 q.lower() 是把 SCORE_MAP 的 key 轉小寫去找 parameters
        # 如果你的 parameters 名稱不同，這裡要改成對應的名稱，例如：
        # ans = params.get("q1_answer", "skip")  # 針對 Q1
        ans = params.get("q1_answer", "skip") # <-- 可能要改成你自己的 parameter 名稱
        ans = params.get("q2_answer", "skip")
        total_score += mapping.get(ans, 0)
        print(f"[DEBUG] {q} answer={ans}, current total={total_score}")

    # =========================
    # Ending Intent 回傳總分
    # 注意：如果你的 Ending Intent 名稱不是 "Ending"，這裡也要改
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






