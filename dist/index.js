// server/index.ts
import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import axios from "axios";
var __dirname = path.dirname(fileURLToPath(import.meta.url));
var app = express();
var PORT = 5e3;
app.use(express.json());
var PYTHON_BACKEND_URL = "http://127.0.0.1:5001";
function filterHeaders(headers) {
  const filtered = {};
  const allowList = ["authorization", "content-type", "accept"];
  for (const key in headers) {
    if (allowList.includes(key.toLowerCase())) {
      filtered[key] = headers[key];
    }
  }
  return filtered;
}
var proxyToPython = async (req, res) => {
  try {
    const targetUrl = `${PYTHON_BACKEND_URL}${req.originalUrl}`;
    console.log(`[\uD504\uB85D\uC2DC] ${req.method} ${req.originalUrl} \u2192 ${targetUrl}`);
    const headers = filterHeaders(req.headers);
    const axiosConfig = {
      method: req.method,
      url: targetUrl,
      headers,
      data: req.method !== "GET" ? req.body : void 0,
      validateStatus: () => true
      // 에러 상태도 수동 처리
    };
    const response = await axios(axiosConfig);
    const contentType = response.headers["content-type"];
    if (contentType && contentType.includes("application/json")) {
      res.status(response.status).json(response.data);
    } else {
      res.status(response.status).send(response.data);
    }
  } catch (error) {
    console.error("\u274C Python FastAPI \uD504\uB85D\uC2DC \uC624\uB958:", error.message);
    res.status(500).json({ error: "Python FastAPI \uC5F0\uACB0 \uC2E4\uD328", details: error.message });
  }
};
app.use("/api/*", proxyToPython);
app.use("/health", proxyToPython);
if (process.env.NODE_ENV === "production") {
  app.use(express.static("dist/public"));
}
app.get("*", (req, res) => {
  if (!req.path.startsWith("/api") && !req.path.startsWith("/health")) {
    res.send(`
      <!DOCTYPE html>
      <html lang="ko">
      <head>
        <meta charset="UTF-8" />
        <title>Chat Toner - \uD504\uB85D\uC2DC \uC11C\uBC84</title>
        <style>
          body { font-family: sans-serif; background: #f0f0f0; padding: 40px; }
          .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>\u2705 Chat Toner \uD504\uB85D\uC2DC \uC11C\uBC84 \uC815\uC0C1 \uC791\uB3D9 \uC911</h1>
          <p>Python \uBC31\uC5D4\uB4DC\uC640 \uC5F0\uACB0\uB428 (FastAPI @ \uD3EC\uD2B8 5001)</p>
          <p>\uD504\uB85D\uC2DC \uC11C\uBC84 \uD3EC\uD2B8: 5000</p>
          <p><a href="/health">/health \uC0C1\uD0DC \uD655\uC778</a></p>
        </div>
      </body>
      </html>
    `);
  }
});
app.listen(PORT, () => {
  console.log(` \uD504\uB85D\uC2DC \uC11C\uBC84 \uC2E4\uD589 \uC911: http://localhost:${PORT}`);
  console.log(` \uBAA8\uB4E0 /api/* \uC694\uCCAD\uC740 Python FastAPI(5001)\uB85C \uC804\uB2EC\uB429\uB2C8\uB2E4.`);
});
