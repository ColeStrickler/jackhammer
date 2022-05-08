import re
import requests


phone_extract = re.compile('\S+@[a-z]+\.[a-z]{3}')

response = requests.get("https://budibase.com/components")

text = response.text + " colestrickler@gmail.com"

print(re.findall(phone_extract, text))