import requests
import re

phone = re.compile('\+?[0-9]?-?\(?[0-9]*\)?-[0-9]+-[0-9]+')

response = requests.get("https://www.ups.com/us/en/support/contact-us.page")
search = re.findall(phone, response.text)
print(response.text)
print(search)