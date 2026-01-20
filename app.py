from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    print("收到 Dialogflow request:", req)
    return jsonify({"fulfillmentText": "Webhook 成功連線！🚀"})










