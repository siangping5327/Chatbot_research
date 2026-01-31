from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# SCORE_MAP：定義要計分的題目
# 只做 Q1 + Q2，其他題目不在此 map 就不計分
# key = Dialogflow parameter 名稱
# value = 各選項對應分數
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
    # 非問題題目且非 Ending Intent → 不做計分
    # 這樣第三題到第十題雖然沒計分，也不會中斷對話
    # =========================
    if not params and intent.lower() != "ending":
        print("[DEBUG] Non-question intent or no parameters, skipping score calculation")
        return jsonify({"fulfillmentText": ""})

    # =========================
    # 計算總分（只計 SCORE_MAP 內的題目）
    # =========================
    total_score = 0
    debug_answers = {}

    for question, options in SCORE_MAP.items():
        ans = params.get(question, "skip")  # 如果參數不存在，就 skip
        score = options.get(ans, 0)
        total_score += score
        debug_answers[question] = {
            "answer": ans,
            "score": score,
            "running_total": total_score
        }
        print(f"[DEBUG] {question}: answer={ans}, score={score}, total_score={total_score}")

    # =========================
    # Ending Intent 回傳總分
    # =========================
    if intent.lower() == "ending":
        print(f"[DEBUG] Final total score={total_score}")
        return jsonify({
            "fulfillmentText": f"您的科技頸風險總分為 {total_score} 分"
        })

    # =========================
    # 非 Ending Intent 回傳確認訊息（開發用 debug）
    # 對話不中斷
    # =========================
    return jsonify({
        "fulfillmentText": f"已記錄您的回答：{debug_answers}"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)






