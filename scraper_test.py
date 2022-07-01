from attr import attr
from bs4 import BeautifulSoup
from urllib.request import urlopen

TARGET_HOME = "https://www.target.com"

target_url = TARGET_HOME

page = urlopen(target_url)
html = page.read().decode("utf-8")

soup = BeautifulSoup(html, "html.parser")
body = soup.body
print(body)

