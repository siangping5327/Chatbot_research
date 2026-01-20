from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    
    # 印出收到的資料到 Railway log
    print("===== Dialogflow request =====")
    print(req)
    
    # 回傳簡單訊息給 Dialogflow
    return jsonify({
        "fulfillmentText": "Webhook 成功連線！🚀"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)







