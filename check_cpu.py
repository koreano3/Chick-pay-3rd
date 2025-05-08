# CloudWatch에서 리소스(CPU/Memory/Network) 메트릭 수집하기
import json
import sys

with open('cpu_result.json') as f:
    data = json.load(f)

datapoints = data['Datapoints']
cpu_usages = [point['Average'] for point in datapoints]
# CPU 사용률 리스트화 

max_cpu = max(cpu_usages)
print(f"Max CPU Usage: {max_cpu}%")
if max_cpu > 80:
    print("❌ CPU 80% 초과: 실패")
    sys.exit(1)
    # 최고 CPU 사용률이 80% 넘으면 Drone 실패 처리
else:
    print("✅ CPU 정상 범위")