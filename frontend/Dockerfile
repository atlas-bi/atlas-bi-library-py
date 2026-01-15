FROM node:21 AS builder

ENV NEXT_TELEMETRY_DISABLED=1

RUN npm install -g pnpm

WORKDIR /app

COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/web/package.json ./apps/web/package.json
COPY packages/types/package.json ./packages/types/package.json
COPY packages/ui/package.json ./packages/ui/package.json

RUN pnpm install -r --frozen-lockfile

COPY . .

RUN pnpm --filter web build


FROM node:21 AS runner

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

RUN npm install -g pnpm

WORKDIR /app

COPY --from=builder /app /app

EXPOSE 3000
