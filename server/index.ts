import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import axios from "axios";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 5003;

app.use(express.json());

// Python 백엔드 URL
const PYTHON_BACKEND_URL =
  process.env.FASTAPI_URL ?? "http://127.0.0.1:5001";

// 안전한 헤더 필터링
function filterHeaders(headers: any) {
  const filtered: any = {};
  const allowList = ["authorization", "content-type", "accept"];
  for (const key in headers) {
    if (allowList.includes(key.toLowerCase())) {
      filtered[key] = headers[key];
    }
  }
  return filtered;
}

// Python FastAPI로 프록시하는 함수
const proxyToPython = async (req, res) => {
  try {
    // /api/* 경로를 /api/v1/* 경로로 매핑
    let targetPath = req.originalUrl;
    if (req.originalUrl.startsWith('/api/') && !req.originalUrl.startsWith('/api/v1/')) {
      targetPath = req.originalUrl.replace('/api/', '/api/v1/');
    }
    
    const targetUrl = `${PYTHON_BACKEND_URL}${targetPath}`;
    console.log(`[프록시] ${req.method} ${req.originalUrl} → ${targetUrl}`);

    const headers = filterHeaders(req.headers);

    const axiosConfig = {
      method: req.method,
      url: targetUrl,
      headers,
      data: req.method !== "GET" ? req.body : undefined,
      validateStatus: () => true, // 에러 상태도 수동 처리
    };

    const response = await axios(axiosConfig);

    const contentType = response.headers["content-type"];
    if (contentType && contentType.includes("application/json")) {
      res.status(response.status).json(response.data);
    } else {
      res.status(response.status).send(response.data);
    }
  } catch (error) {
    console.error("❌ Python FastAPI 프록시 오류:", error.message);
    res
      .status(500)
      .json({ error: "Python FastAPI 연결 실패", details: error.message });
  }
};

// API 요청을 Python FastAPI로 프록시
app.use("/api/*", proxyToPython);
app.use("/health", proxyToPython);

// 프로덕션 환경 정적 파일 제공
if (process.env.NODE_ENV === "production") {
  app.use(express.static("dist/public"));
}

// 기타 라우트: 상태 확인 페이지
app.get("*", (req, res) => {
  if (!req.path.startsWith("/api") && !req.path.startsWith("/health")) {
    res.send(`
      <!DOCTYPE html>
      <html lang="ko">
      <head>
        <meta charset="UTF-8" />
        <title>Chat Toner - 프록시 서버</title>
        <style>
          body { font-family: sans-serif; background: #f0f0f0; padding: 40px; }
          .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>✅ Chat Toner 프록시 서버 정상 작동 중</h1>
          <p>Python 백엔드와 연결됨 (FastAPI @ 포트 5001)</p>
          <p>프록시 서버 포트: 5000</p>
          <p><a href="/health">/health 상태 확인</a></p>
        </div>
      </body>
      </html>
    `);
  }
});

app.listen(PORT, () => {
  console.log(` 프록시 서버 실행 중: http://localhost:${PORT}`);
  console.log(` 모든 /api/* 요청은 Python FastAPI(5001)로 전달됩니다.`);
});
