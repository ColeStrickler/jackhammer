import requests


response = requests.get("http://google.com")
print(response)
print(response.elapsed.total_seconds() * 1000)