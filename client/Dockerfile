# ---------- Build stage ----------
FROM node:20-alpine AS builder
WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm ci

# 소스 복사
COPY . .

# (선택) 빌드 시 API URL 주입: import.meta.env.VITE_API_URL 로 사용
ARG VITE_API_URL
RUN if [ -n "$VITE_API_URL" ]; then echo "VITE_API_URL=$VITE_API_URL" > .env.production; fi

# 빌드 (dist/ 생성)
RUN npm run build

# ---------- Runtime (Nginx) ----------
FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html

# SPA 라우팅/헬스체크 설정
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 정적 산출물만 복사
COPY --from=builder /app/dist/ ./

EXPOSE 8080

# 컨테이너 내부 헬스체크 (ALB 헬스체크는 /healthz 사용)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -qO- http://localhost:8080/healthz || exit 1
