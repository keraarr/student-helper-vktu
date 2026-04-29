import requests

url = "https://www.do.ektu.kz/PReports/Schedule/ScheduleGroup.asp"
response = requests.get(url, timeout=20)

response.encoding = "utf-8"

print(response.status_code)
print(response.text[:2000])
