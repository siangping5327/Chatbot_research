from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 題目分數表（示範 Q1 + Q2，可延伸更多題）
# key = Dialogflow parameter 名稱
# value = 每個選項對應分數
# =========================
SCORE_MAP = {
    "q1_answer": {  
        "short": 0,
        "medium": 1,
        "long": 2,
        "skip": 0
    },
    "q2_answer": {  
        "true": 2,
        "false": 1,
        "skip": 0
    }
}

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    intent = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})

    print(f"[DEBUG] intent={intent}")
    print(f"[DEBUG] full request body: {req}")

    # =========================
    # 計算總分
    # =========================
    total_score = 0
    debug_answers = {}

    for question, options in SCORE_MAP.items():
        ans = params.get(question, "skip")  # 如果使用者沒回答，預設 skip
        score = options.get(ans, 0)
        total_score += score
        debug_answers[question] = {
            "answer": ans,
            "score": score,
            "running_total": total_score
        }
        print(f"[DEBUG] {question}: answer={ans}, score={score}, total_score={total_score}")

    # =========================
    # 如果是 Ending Intent，回傳總分
    # =========================
    if intent.lower() == "ending":  # 不分大小寫
        print(f"[DEBUG] Final total score={total_score}")
        return jsonify({
            "fulfillmentText": f"您的科技頸風險總分為 {total_score} 分"
        })

    # =========================
    # 非 Ending Intent 回傳確認訊息
    # =========================
    return jsonify({
        "fulfillmentText": f"已記錄您的回答：{debug_answers}"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
