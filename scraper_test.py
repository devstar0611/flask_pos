from attr import attr
from bs4 import BeautifulSoup
from urllib.request import urlopen

TARGET_HOME = "https://www.target.com/"

target_url = TARGET_HOME

page = urlopen(target_url)
html = page.read().decode("utf-8")

soup = BeautifulSoup(html, "html.parser")
categoryMenu = soup.find("div", attrs={"data-test": "@web/CategoryMenu"})
print(type(categoryMenu[0]))
span_categories = categoryMenu.find_all(
    "span", attrs={"class": "CellSkinny__TextWrapper-sc-117d15w-0 bcbdds"})
for category in span_categories:
    print(category.string)
    print(category.parent.parent["href"])
