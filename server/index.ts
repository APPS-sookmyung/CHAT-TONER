import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5000;
const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:5005';

// CORS middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');

  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'express-proxy' });
});

// Proxy ALL requests to Python backend (except health)
app.use('/', createProxyMiddleware({
  target: PYTHON_BACKEND_URL,
  changeOrigin: true,
  filter: (pathname) => pathname.startsWith('/api'),
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.status(500).json({ error: 'Proxy error', message: err.message });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`Proxying ${req.method} ${req.url} to ${PYTHON_BACKEND_URL}${proxyReq.path}`);
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`Response from backend: ${proxyRes.statusCode} for ${req.method} ${req.url}`);
  }
}));

// Serve static files in production
if (process.env.NODE_ENV === 'production') {
  const distPath = path.join(__dirname, '../dist/public');
  app.use(express.static(distPath));

  // Catch-all handler for React Router
  app.get('*', (req, res) => {
    res.sendFile(path.join(distPath, 'index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`Express proxy server running on port ${PORT}`);
  console.log(`Proxying API requests to: ${PYTHON_BACKEND_URL}`);
});