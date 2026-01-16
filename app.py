from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 暫存使用者狀態（測試用）
user_states = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    session = data.get("session")
    intent = data.get("queryResult", {}).get("intent", {}).get("displayName")
    params = data.get("queryResult", {}).get("parameters", {})

    # 初始化或取得使用者狀態
    state = user_states.get(session, {"score": 0})

    # Q1
    if intent == "Q1":
        answer = params.get("answer")
        if answer == "long":
            state["score"] += 2
        elif answer == "medium":
            state["score"] += 1

    # Q2
    elif intent == "Q2":
        answer = params.get("answer")
        if answer == "true":
            state["score"] += 2
        elif answer == "false":
            state["score"] += 1

    user_states[session] = state

    # 結尾
    if intent == "Finish":
        score = state["score"]
        if score >= 3:
            risk = "高風險"
        elif score >= 1:
            risk = "中風險"
        else:
            risk = "低風險"

        return jsonify({
            "fulfillmentText": f"根據你的回答，你的風險等級為【{risk}】。"
        })

    return jsonify({"fulfillmentText": "已記錄，請繼續。"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
