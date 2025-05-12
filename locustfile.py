import random
import string
from locust import HttpUser, task, between

class ChickPayUser(HttpUser):
    host = "https://chick-pay.com"
    wait_time = between(1, 2)

    def on_start(self):
        # 1. 랜덤 유저 정보 생성
        rand_suffix = ''.join(random.choices(string.digits, k=6))
        self.email = f"loadtest_{rand_suffix}@a111.com"
        self.password = "Ab123456"
        self.name = "부하테스트"
        self.birthdate = "1995-01-01"

        # 2. 회원가입 요청
        signup_payload = {
            "email": self.email,
            "name": self.name,
            "birthdate": self.birthdate,
            "password1": self.password,
            "password2": self.password
        }

        signup_response = self.client.post("/zapp/api/register/", json=signup_payload)

        if signup_response.status_code in [200, 201]:
            print(f"✅ 회원가입 성공: {self.email}")
        elif signup_response.status_code == 400 and "email" in signup_response.text:
            print(f"⚠️ 이미 존재 (무시): {self.email}")
        else:
            print(f"❌ 회원가입 실패: {self.email} | 응답: {signup_response.status_code} | {signup_response.text}")
            raise Exception("회원가입 실패")

        # 3. 로그인 요청
        login_response = self.client.post("/zapp/api/login/", json={
            "email": self.email,
            "password": self.password
        })

        if login_response.status_code != 200:
            print(f"❌ 로그인 실패: {self.email} | 응답: {login_response.status_code} | {login_response.text}")
            raise Exception("로그인 실패")

        self.session_cookie = login_response.cookies.get('sessionid')
        self.csrf_token = login_response.cookies.get('csrftoken')

    @task
    def hit_main_page(self):
        headers = {
            "Cookie": f"sessionid={self.session_cookie}; csrftoken={self.csrf_token}",
            "X-CSRFToken": self.csrf_token
        }
        self.client.get("/", headers=headers)