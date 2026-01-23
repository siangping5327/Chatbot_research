from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 分數對照表（SCORE_MAP）
# =========================
SCORE_MAP = {
    "Q2": {"long": 2, "medium": 1, "short": 0, "skip": 0},
    "Q3": {"true": 2, "false": 1, "skip": 0}
}

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    intent = req["queryResult"]["intent"]["displayName"]

    # =========================
    # 嘗試讀取使用者的 answer
    # =========================
    params = req["queryResult"].get("parameters", {})
    answer = params.get("answer") or req["queryResult"].get("queryText", "").strip().lower()
    
    # =========================
    # 🔹 debug：確認 queryText 與 answer
    print(f"[DEBUG] queryText={req['queryResult']['queryText']}")
    print(f"[DEBUG] answer={answer}")

    # =========================
    # 讀取 score-session context（若不存在則初始化）
    # =========================
    output_contexts = req["queryResult"].get("outputContexts", [])
    state = {"score": 0}
    for ctx in output_contexts:
        if ctx["name"].endswith("/contexts/score-session"):
            state = ctx.get("parameters", {"score": 0})
            if "score" not in state:
                state["score"] = 0





















