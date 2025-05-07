# Locust 테스트 결과를 검증 (응답속도, 에러율 체크)
import pandas as pd
import sys

df = pd.read_csv('locust_result_stats.csv')

# 평균 응답시간 체크 (응답시간 1초 넘으면 실패)
avg_response_time = df[df['Name'] == "Total"]["Average Response Time"].values[0]
if avg_response_time > 1000:
    print(f"❌ 평균 응답시간 {avg_response_time}ms 초과: 실패")
    sys.exit(1)

# 에러율 체크  (에러율 2% 초과면 실패)
failure_count = df[df['Name'] == "Total"]["Failure Count"].values[0]
request_count = df[df['Name'] == "Total"]["Request Count"].values[0]
error_rate = (failure_count / request_count) * 100

if error_rate > 2:
    print(f"❌ 에러율 {error_rate}% 초과: 실패")
    sys.exit(1)

print("✅ 성능 기준 통과")
