# 1단계: 빌드
FROM node:18 AS build
WORKDIR /app
COPY . ./
RUN npm install
RUN npm run build

# 2단계: Nginx로 정적 파일 서빙
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]