from flask import Flask, request
import os

app = Flask(__name__)

# 測試路由，Dialogflow webhook 可以呼叫這個
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    
    # 你可以在這裡做計算風險或其他邏輯
    response_text = "Webhook 接收到訊息！"
    
    # 回傳給 Dialogflow 的格式
    return jsonify({"fulfillmentText": response_text})

# 這段確保平台能正常啟動 Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway 會給你 PORT
    app.run(host="0.0.0.0", port=port)



