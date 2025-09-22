# nestjs-gateway/Dockerfile

FROM node:20-alpine AS builder
WORKDIR /app

RUN apk add --no-cache python3 make g++ libc6-compat

# 의존성 먼저 설치(캐시 활용)
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

RUN npm prune --ombit=dev

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000

RUN apk add --no-cache tini

# COPY package*.json ./
# RUN npm ci --omit=dev

# COPY --from=builder /app/dist ./dist

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/dist ./dist

USER node
EXPOSE 3000
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/main.js"]