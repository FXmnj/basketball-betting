#!/bin/sh
# Generate Prisma client if needed
if [ ! -d "/app/node_modules/.prisma/client" ]; then
  echo "Generating Prisma client..."
  npx prisma generate
fi

# Start the application
exec node dist/index.js
