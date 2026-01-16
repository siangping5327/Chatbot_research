from flask import Flask, request
import os

app = Flask(__name__)

# 測試路由 這是 webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    print("Webhook 收到資料！", request.get_json())
    return jsonify({"fulfillmentText": "收到"})


# 這段確保平台能正常啟動 Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway 會給你 PORT
    app.run(host="0.0.0.0", port=port)





