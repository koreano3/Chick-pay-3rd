   # React 앱 빌드를 위한 단계 추가 필요
   FROM node:16 as frontend
   WORKDIR /app/frontend
   COPY react-app/package*.json ./
   RUN npm install
   COPY react-app/ .
   RUN npm run build

   # Django 서버
   FROM python:3.10
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   COPY --from=frontend /app/frontend/build ./static/
   EXPOSE 8000
   CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]