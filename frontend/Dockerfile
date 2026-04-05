FROM node:20-alpine

WORKDIR /app

RUN npm install -g serve@14.2.4 \
 && printf '%s\n' '<!doctype html><html><head><meta charset="utf-8"><title>AppLens</title></head><body><h1>AppLens frontend container</h1></body></html>' > /app/index.html

EXPOSE 3000

CMD ["serve", "-s", "/app", "-l", "3000"]
