# nestjs-gateway/Dockerfile
# =====================================================
# 1. 빌드(Builder) 스테이지: 앱을 빌드하는 역할만 수행
# =====================================================
FROM node:20 AS builder

WORKDIR /app

# 1. package.json을 먼저 복사하여 의존성만 설치 (레이어 캐시 활용 극대화)
COPY package*.json ./
RUN npm install

# 2. 의존성 설치가 끝난 후, 전체 소스 코드를 복사
COPY . .

# 3. 애플리케이션 빌드
RUN npm run build

# =====================================================
# 2. 프로덕션(Production) 스테이지: 빌드된 앱을 실행하는 역할만 수행
# =====================================================
FROM node:20

WORKDIR /app

# 1. 빌드 스테이지에서 설치한 node_modules를 복사
COPY --from=builder /app/node_modules ./node_modules

# 2. 빌드 스테이지에서 빌드된 결과물(dist 폴더)을 복사
COPY --from=builder /app/dist ./dist

# 3. 앱 실행
CMD ["node", "dist/main"]