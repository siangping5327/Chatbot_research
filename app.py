from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    print("收到 Dialogflow request:", req)
    return jsonify({"fulfillmentText": "Webhook 成功連線！🚀"})

# ======================================
# Railway 正確啟動方式
# ======================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)









