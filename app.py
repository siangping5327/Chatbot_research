// 引入套件
const express = require("express");
const bodyParser = require("body-parser");

// 建立 Express app
const app = express();
app.use(bodyParser.json()); // 解析 JSON

// Webhook route
app.post("/webhook", (req, res) => {
  // 完整 request
  console.log("Request body:", JSON.stringify(req.body, null, 2));

  // 讀取 Q1 的參數
  const q1Answer = req.body.queryResult?.parameters?.q1_answer || "沒有抓到";
  console.log("Q1 answer:", q1Answer);

  // 回傳訊息給 Dialogflow
  res.json({
    fulfillmentText: `你點的按鈕是: ${q1Answer}`
  });
});

// 啟動 server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Webhook server is running on port ${PORT}`);
});




   



   





