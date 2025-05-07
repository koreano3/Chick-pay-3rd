import pyotp
import time
from locust import HttpUser, task, between

class ChickPayUser(HttpUser):
    host = "https://chick-pay.com"
    wait_time = between(1, 2)

    def on_start(self):
        response = self.client.post("/zapp/api/login/", json={
            "email": "eomsigi@gmail.com",
            "password": "123123"
        })
        if response.status_code != 200:
            print(f"status: {response.status_code}")
            print(f"body: {response.text}")
            raise Exception("로그인 실패")

        self.session_cookie = response.cookies.get('sessionid')
        self.csrf_token = response.cookies.get('csrftoken')

         # ✅ 30초 경계 피하기
        while True:
            seconds = time.gmtime().tm_sec % 30
            if 2 <= seconds <= 27:
                break
            time.sleep(0.3)

        # ✅ OTP 생성
        totp = pyotp.TOTP("47GE56Q72WHDBFSMAMUHKKXIJPSQZRUT", interval=30)

        # 현재 OTP + 과거 OTP 코드 모두 준비
        current_otp = totp.now()
        previous_otp = totp.at(int(time.time()) - 30)

        print(f"✅ 현재 OTP: {current_otp}, 과거 OTP: {previous_otp}")

        headers = {
            "Cookie": f"sessionid={self.session_cookie}; csrftoken={self.csrf_token}",
            "X-CSRFToken": self.csrf_token
        }

        # ✅ 먼저 현재 OTP로 시도
        otp_response = self.client.post("/zapp/api/otp/verify/", json={
            "otp_code": current_otp
        }, headers=headers)

        if otp_response.status_code != 200:
            print(f"❌ 현재 OTP 실패, 과거 OTP로 재시도...")

            # 과거 OTP로 다시 시도
            otp_response = self.client.post("/zapp/api/otp/verify/", json={
                "otp_code": previous_otp
            }, headers=headers)

            if otp_response.status_code != 200:
                print(f"❌ 과거 OTP도 실패! status_code: {otp_response.status_code}, response: {otp_response.text}")
                raise Exception(f"OTP 인증 실패: {otp_response.text}")

        self.auth_headers = headers

    @task
    def deposit(self):
        self.client.post("/zapp/api/cash/deposit/", json={
            "amount": 10000
        }, headers=self.auth_headers)

    @task
    def withdraw(self):
        self.client.post("/zapp/api/cash/withdraw/", json={
            "amount": 5000
        }, headers=self.auth_headers)

    @task
    def transfer(self):
        self.client.post("/zapp/api/cash/transfer/", json={
            "receiver_email": "a125@a125.com",
            "amount": 2000
        }, headers=self.auth_headers)

    @task
    def transactions(self):
        self.client.get("/zapp/api/transactions/", headers=self.auth_headers)
