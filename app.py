from flask import Flask, request, jsonify

app = Flask(__name__)

# 每個選項對應的分數
SCORE_MAP = {
    "少於 3 小時": 0,
    "3–6 小時": 1,
    "6 小時以上": 2,
    "是": 2,
    "否，會低頭": 2
}

def get_result_text(total_score):
    if total_score >= 4:
        return f"🔴 風險偏高（總分：{total_score}）\n建議您留意使用姿勢，適度休息。"
    elif total_score >= 2:
        return f"🟡 中度風險（總分：{total_score}）\n目前狀況尚可，但仍需注意姿勢。"
    else:
        return f"🟢 低風險（總分：{total_score}）\n目前習慣良好，請繼續保持。"

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)

    intent_name = req["queryResult"]["intent"]["displayName"]
    user_text = req["queryResult"].get("queryText", "")
    params = req["queryResult"].get("parameters", {})

    # 目前累積分數（如果沒有就當 0）
    current_score = params.get("total_score", 0)

    print("Intent:", intent_name)
    print("User text:", user_text)
    print("Current score:", current_score)

    # =========================
    # Ending：顯示總分與結論
    # =========================
    if intent_name == "Ending":
        result_text = get_result_text(current_score)

        return jsonify({
            "fulfillmentText": result_text
        })

    # =========================
    # 一般題目：加分但不顯示訊息
    # =========================
    add_score = SCORE_MAP.get(user_text, 0)
    new_score = current_score + add_score
    params["total_score"] = new_score

    print("Add score:", add_score)
    print("New total:", new_score)

    return jsonify({
        "followupEventInput": {
            "name": "KEEP_CONTEXT",
            "languageCode": "zh-tw",
            "parameters": params
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)









