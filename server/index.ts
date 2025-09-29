import express from "express";
import path from "path";
import axios from "axios";

// For CommonJS compatibility
const __dirname = process.cwd();
const app = express();
const PORT = process.env.PORT || 5003;

app.use(express.json());

// Python backend URL
const PYTHON_BACKEND_URL = process.env.FASTAPI_URL ?? "http://127.0.0.1:5001";

// Safe header filtering
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

// Function to proxy to Python FastAPI
const proxyToPython = async (req: any, res: any) => {
  try {
    // Map /api/* paths to /api/v1/* paths
    let targetPath = req.originalUrl;
    if (
      req.originalUrl.startsWith("/api/") &&
      !req.originalUrl.startsWith("/api/v1/")
    ) {
      targetPath = req.originalUrl.replace("/api/", "/api/v1/");
    }

    const targetUrl = `${PYTHON_BACKEND_URL}${targetPath}`;
    console.log(`[Proxy] ${req.method} ${req.originalUrl} → ${targetUrl}`);

    const headers = filterHeaders(req.headers);

    const axiosConfig = {
      method: req.method,
      url: targetUrl,
      headers,
      data: req.method !== "GET" ? req.body : undefined,
      validateStatus: () => true, // Handle error status manually
    };

    const response = await axios(axiosConfig);

    const contentType = response.headers["content-type"];
    if (contentType && contentType.includes("application/json")) {
      res.status(response.status).json(response.data);
    } else {
      res.status(response.status).send(response.data);
    }
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    console.error("Python FastAPI proxy error:", errorMessage);
    res.status(500).json({
      error: "Python FastAPI connection failed",
      details: errorMessage,
    });
  }
};

// Proxy API requests to Python FastAPI
app.use("/api/*", proxyToPython);
app.use("/health", proxyToPython);

// Serve static files in production environment
if (process.env.NODE_ENV === "production") {
  app.use(express.static("dist/public"));
}

// Other routes: status check page
app.get("*", (req, res) => {
  if (!req.path.startsWith("/api") && !req.path.startsWith("/health")) {
    res.send(`
      <!DOCTYPE html>
      <html lang="ko">
      <head>
        <meta charset="UTF-8" />
        <title>Chat Toner - Proxy Server</title>
        <style>
          body { font-family: sans-serif; background: #f0f0f0; padding: 40px; }
          .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Chat Toner Proxy Server Running</h1>
          <p>Connected to Python backend (FastAPI @ port 5001)</p>
          <p>Proxy server port: 5000</p>
          <p><a href="/health">/health status check</a></p>
        </div>
      </body>
      </html>
    `);
  }
});

app.listen(PORT, () => {
  console.log(`Proxy server running: http://localhost:${PORT}`);
  console.log(`All /api/* requests are forwarded to Python FastAPI (5001).`);
});
