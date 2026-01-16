from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    return {
        "fulfillmentText": "Webhook alive"
    }

if __name__ == "__main__":
    app.run()



