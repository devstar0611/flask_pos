from bs4 import BeautifulSoup
from urllib.request import urlopen

target_url = input("target_url:")

page = urlopen(target_url)
html = page.read().decode("utf-8")

soup = BeautifulSoup(html, "html.parser")
span_categories = soup.find_all(
    "span", attrs={"class": "CellSkinny__TextWrapper-sc-117d15w-0 bcbdds"})
for category in span_categories:
    print(category.string)
    print(category.parent.parent["href"])
