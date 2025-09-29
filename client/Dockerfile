# ---------- Build stage -----# Container internal health check (ALB health check uses /healthz)----
FROM node:20-bookworm AS builder
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source files
COPY . .

# (선택) 빌드 시 API URL 주입: import.meta.env.VITE_API_URL 로 사용
ARG VITE_API_URL
RUN if [ -n "$VITE_API_URL" ]; then echo "VITE_API_URL=$VITE_API_URL" > .env.production; fi

# Build (generate dist/)
RUN npm run build

# ---------- Runtime (Nginx) ----------
FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html

# SPA routing/health check configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy only static assets
COPY --from=builder /app/dist/ ./

EXPOSE 80

# 컨테이너 내부 헬스체크 (ALB 헬스체크는 /healthz 사용)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -qO- http://localhost:80/healthz || exit 1
