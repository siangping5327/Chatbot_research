from flask import Flask, request, jsonify

# 建立 Flask Web Server（Dialogflow Webhook 的接收端）
app = Flask(__name__)

# ======================================================
# 題目設定區（Question Configuration）
# ------------------------------------------------------
"""
設計原則：
- 每一題都有一個「對應的 answer context」
- webhook 不看 intent 名稱來算分
- webhook 只根據 context → 推論是哪一題被回答
"""

"""
命名邏輯：
-Q1 → context = Q1_ANS
-Q2 → context = Q2_ANS

好處：
- 永遠不會因 intent 跳轉而分數錯位
- 新增題目只需擴充這個 dict   
 """
# ======================================================
QUESTION_CONFIG = {
    "Q1": {
        # Q1 的答案完成後，Dialogflow 會產生的 context
        "context": "Q1_ANS",

        # 使用者「實際點選的文字」→ 標準化代碼
        # （避免直接用中文算分，方便維護與分析）
        "text_map": {
            "少於 3 小時": "short",
            "3–6 小時": "medium",
            "6 小時以上": "long",
            "略過/不願透露": "skip"
        },

        # 標準化代碼 → 分數
        "score_map": {
            "short": 0,
            "medium": 1,
            "long": 2,
            "skip": 0
        }
    },

    "Q2": {
        "context": "Q2_ANS",

        "text_map": {
            "是": "true",
            "否，會低頭": "false",
            "略過": "skip"
        },

        "score_map": {
            "true": 1,
            "false": 2,
            "skip": 0
        }
    }
}

# ======================================================
"""
# 根據 context 判斷「上一題是哪一題」
# ------------------------------------------------------
# 核心概念：
# - 使用者選擇 Q1 的選項
# - 命中的是「下一個 intent（Q2）」
# - 但 request 內仍會帶著 Q1_ANS context
#
# 此函式的工作：
# - 掃描 request 中所有 outputContexts
# - 找出哪一個 context 對應 QUESTION_CONFIG
# - 回傳被回答的題目代號（Q1 / Q2 / ...） 
"""
# ======================================================

def find_answered_question(req):
    for qid, cfg in QUESTION_CONFIG.items():
        # Dialogflow context 在 JSON 中的完整結尾名稱
        ctx_suffix = f"/contexts/{cfg['context']}"

        # 掃描 request 中所有 contexts
        for ctx in req["queryResult"].get("outputContexts", []):
            if ctx["name"].endswith(ctx_suffix):
                return qid  # 找到即回傳題號

    return None  # 沒找到任何可計分的題目


# ======================================================
# Webhook 主入口（Dialogflow 呼叫這裡）
# ======================================================
@app.route("/webhook", methods=["POST"])
def webhook():
    # 取得 Dialogflow 傳來的 request JSON
    req = request.get_json()

    # 使用者實際輸入或點選的文字
    raw_text = req["queryResult"]["queryText"].strip()
    print(f"[DEBUG] raw_text={raw_text}")

    # ==================================================
    # 讀取或初始化 score-session（累積分數）
    # --------------------------------------------------
    """ 
      設計說明：
      - 分數不存在 DB，而是存在 Dialogflow context
      - 每一輪 webhook 都從 context 取回目前分數 
    """
    # ==================================================
    state = {"score": 0}

    for ctx in req["queryResult"].get("outputContexts", []):
        if ctx["name"].endswith("/contexts/score-session"):
            # 如果已有 score-session，讀取既有分數
            state = ctx.get("parameters", {"score": 0})
            state.setdefault("score", 0)

    # ==================================================
    # 判斷這一次「實際被回答的是哪一題」
    # --------------------------------------------------
    # 注意：
    # - 不使用 intent 名稱
    # - 只根據 context 對齊題目
    # ==================================================
    qid = find_answered_question(req)

    if qid:
        cfg = QUESTION_CONFIG[qid]

        # 將使用者文字轉為標準化代碼
        value = cfg["text_map"].get(raw_text, "skip")

        # 根據代碼取得分數
        score_added = cfg["score_map"].get(value, 0)

        # 累積總分
        state["score"] += score_added

        print(
            f"[DEBUG] answered={qid}, "
            f"value={value}, "
            f"add={score_added}, "
            f"total={state['score']}"
        )
    else:
        # 通常發生在非題目 intent（例如歡迎訊息）
        print("[DEBUG] no answered question context found")

    # ==================================================
    """Ending intent：顯示總分並清除 session
    
     Ending 不再加分，只負責呈現結果 """
    # ==================================================
    intent = req["queryResult"]["intent"]["displayName"]
    if intent == "Ending":
        return jsonify({
            "fulfillmentText": f"您的科技頸風險總分為 {state['score']} 分",
            "outputContexts": [
                {
                    # lifespan = 0 → 清除 score-session
                    "name": f"{req['session']}/contexts/score-session",
                    "lifespanCount": 0,
                    "parameters": {}
                }
            ]
        })

    # ==================================================
    # 非 Ending：回存更新後的分數
    # --------------------------------------------------
    # 讓下一題 webhook 可以繼續累積
    # ==================================================
    return jsonify({
        "outputContexts": [
            {
                "name": f"{req['session']}/contexts/score-session",
                "lifespanCount": 50,
                "parameters": state
            }
        ]
    })

# ======================================================
# 本地或雲端啟動 Flask 服務
# ======================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


   


