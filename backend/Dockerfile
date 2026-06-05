# Backend Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Install OpenSSL development libraries for Prisma engine compatibility
RUN apk add --no-cache openssl openssl-dev

# Copy package files
COPY backend/package*.json ./
COPY backend/tsconfig.json ./
COPY backend/src ./src
COPY backend/prisma ./prisma

# Install dependencies
RUN npm install --legacy-peer-deps

# Clean and regenerate Prisma client with correct binary target
RUN rm -rf node_modules/.prisma/client
RUN npx prisma generate

# Build TypeScript
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

# Install OpenSSL for Prisma compatibility
RUN apk add --no-cache openssl

# Copy all node_modules from builder (includes all generated Prisma client files)
COPY --from=builder /app/node_modules ./node_modules

# Copy package files
COPY backend/package*.json ./

# Copy Prisma schema
COPY backend/prisma ./prisma

# Copy built application
COPY --from=builder /app/dist ./dist

EXPOSE 5000

CMD ["node", "dist/index.js"]
