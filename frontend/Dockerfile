# ============================================================
# Frontend Dockerfile — Multi-stage build
#
# Stage 1 (builder): Installs deps and builds the Next.js app
# Stage 2 (runner):  Copies only the built output — no node_modules
#
# WHY multi-stage? Cuts the final image from ~1.2GB to ~250MB.
# The build artifacts are all Next.js needs to serve the app.
# ============================================================

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm ci --frozen-lockfile

# Copy source and build
COPY . .

# Inject build-time env vars (NEXT_PUBLIC_* are baked into the bundle)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_WS_URL=ws://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL

RUN npm run build

# Stage 2: Production runner
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Only copy what's needed to run the app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
