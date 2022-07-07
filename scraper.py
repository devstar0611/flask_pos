from googleapiclient.discovery import build

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

import settings
import requests 
import json 
import html
import os
import pathlib
import time
from selectorlib import Extractor

import urllib.request

## start mine
import pyppeteer
import bs4
import asyncio
import sqlite3
import sys
import datetime

## end mine





profilePath= "C:\\Users\\justs\\AppData\\Local\\Google\\Chrome\\User Data"

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--ignore-certificate-errors")
options.add_argument("--log-level=3")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
#options.add_argument("user-data-dir="+ profilePath)

print("insdide scrapper")

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "static/data", "categories.json")
config_url = os.path.join(SITE_ROOT, "static/data", "config.json")
# my_api_key = "AIzaSyAqKIVgIszDr31O03_FmZ0zvJ_KN2y2UUM"
# my_cse_id = "6e8803333f47a47db"

#############
TARGET_HOMEPAGE = "https://www.target.com"

async def update_db():

    conn = sqlite3.connect('mydb.db')
    cur = conn.cursor()
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    # start - get all information of all products from target.com
    sys.stdout = open('log.txt', 'w+')
    print("---------------------------------------------------------------------------------------")
    print(datetime.datetime.today())
    print("====================================================================================")

    categories = []
    subcategories = []
    sub_subcategories = []
    products = []
    products_count = []
    browser = await pyppeteer.launch(
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False)
    page = await browser.newPage()

    await page.goto("https://www.target.com/c/shop-all-categories/-/N-5xsxf")
    content = await page.content()
    soup = bs4.BeautifulSoup(content, features="lxml")

    # start - finding categories list
    components = soup.select('div[data-component-type="Browse - Manual"]')
    print(len(components))
    for comp in components:
        # soup = bs4.BeautifulSoup(str(comp), features="lxml")
        # soup = bs4.BeautifulSoup(soup.select(
        #    'div.children')[0], features="lxml")
        try:
            children = comp.select('div.children')[0].contents
        except:
            children = comp.select('ul')[0].contents
        print(len(children))
        for category in children:
            category_name = category.a.text
            category_url = category.a['href']
            if category_url.find("http") < 0:
                category_url = TARGET_HOMEPAGE + category_url
            print(category_name, category_url)
            categories.append({
                'name': category_name,
                'url': category_url
            })

    # categories = json.load(open(os.path.join("categories.json")))
    # print(categories)
    jsonString = json.dumps(categories)
    jsonFile = open("categories.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()
    # end - finding categories list

    # start - finding subcategories or products list
    for category in categories:
        print("category=", category)
        category_name = category['name']
        category_url = category['url']
        await page.goto(category_url)
        await asyncio.sleep(5)
        content = await page.content()
        soup = bs4.BeautifulSoup(content, features="lxml")
        products_grid = soup.select('div[data-test="product-grid"] section>div')
        print("products_grid find?=", len(products_grid))
        if len(products_grid):
            # start - finding products in category
            print("start - finding products in category")
            # print(soup.select('h2[data-test="resultsHeading"]'))
            try:
                results_count = int(soup.select('h2[data-test="resultsHeading"]')[0].text.split(" ")[0])
            except:
                continue
            print("results_count=", results_count)
            cnt = 0
            page_num = 0
            while cnt <= results_count:
                try:
                    results_count = int(soup.select('h2[data-test="resultsHeading"]')[0].text.split(" ")[0])
                except:
                    break
                # print(category_url + "?Nao=" + str(page_num * 24))
                await page.goto(category_url + "?Nao=" + str(page_num * 24))
                await asyncio.sleep(5)
                content = await page.content()
                soup = bs4.BeautifulSoup(content, features="lxml")
                products_grid = soup.select('div[data-test="product-grid"] section>div')
                print("products_grid find?=", len(products_grid))
                # if not len(products_grid):
                #     content = await page.content()
                #     soup = bs4.BeautifulSoup(content, features="lxml")
                #     products_grid = soup.select('div[data-test="product-grid"] section>div')
                for item in products_grid[0].contents:
                    # print(item)
                    # print(item.text)
                    # print(item.a['href'])
                    # pro = item.select('a[data-test="product-title"]')[0]
                    try:
                        product_name = item.text
                        product_category = category_name
                        product_url = item.a['href']
                    except:
                        continue
                    if product_url.find("http") < 0:
                        product_url = TARGET_HOMEPAGE + product_url
                    products.append({
                        "category": product_category,
                        "name": product_name,
                        "url": product_url
                    })
                    cnt += 1
                    print("product=", cnt,  {
                        "category": product_category,
                        "name": product_name,
                        "url": product_url
                    })
                page_num += 1
                print("page_num=", page_num)
            products_count.append({
                'category': category_name,
                'count': cnt
            })
            print("products_count in this category=", {
                'category': category_name,
                'count': cnt
            })
            print("end - finding products in category")
            # end - finding products in category
        else:
            # start - finding subcategories
            print("start - finding subcategories in category")
            components = soup.select('div[data-component-type="Browse - Manual"]')
            print("components find?=", len(components))
            if len(components):
                for comp in components:
                    # soup = bs4.BeautifulSoup(str(comp), features="lxml")
                    # soup = bs4.BeautifulSoup(soup.select(
                    #    'div.children')[0], features="lxml")
                    try:
                        children = comp.select('div.children')[0].contents
                    except:
                        children = comp.select('ul')[0].contents
                    print("children_cnt=", len(children))
                    for subcategory in children:
                        try:
                            subcategory_name = subcategory.a.text
                            subcategory_url = subcategory.a['href']
                        except:
                            continue
                        if subcategory_url.find("http") < 0:
                            subcategory_url = TARGET_HOMEPAGE + subcategory_url
                        subcategories.append({
                            'parent': category_name,
                            'name': subcategory_name,
                            'url': subcategory_url
                        })
                        print("subcategory=", {
                            'parent': category_name,
                            'name': subcategory_name,
                            'url': subcategory_url
                        })
            print("end - finding subcategories in category")
            # end - finding subcategories

        print("end - finding in category")
        # end - finding subcategories or products list
    print("subcategories=", subcategories)
    jsonString = json.dumps(subcategories)
    jsonFile = open("subcategories.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()
    if len(subcategories):
        # start - finding products in subcategories
        print("start - finding products in subcategories")
        for category in subcategories:
            category_name = category['parent']
            subcategory_name = category['name']
            subcategory_url = category['url']
            print("subcategory=", category)
            await page.goto(subcategory_url)
            await asyncio.sleep(5)
            content = await page.content()
            soup = bs4.BeautifulSoup(content, features="lxml")
            products_grid = soup.select('div[data-test="product-grid"] section>div')
            print("products_grid find?=", len(products_grid))
            if len(products_grid):
                # start - finding products in subcategories
                print("start - finding products in subcategories")
                try:
                    results_count = int(soup.select('h2[data-test="resultsHeading"]')[0].text.split(" ")[0])
                except:
                    continue
                print("results_count=", results_count)
                cnt = 0
                page_num = 0
                while cnt <= results_count:
                    try:
                        results_count = int(soup.select('h2[data-test="resultsHeading"]')[0].text.split(" ")[0])
                    except:
                        break
                    # print(subcategory_url + "?Nao=" + str(page_num * 24))
                    await page.goto(subcategory_url + "?Nao=" + str(page_num * 24))
                    await asyncio.sleep(5)
                    content = await page.content()
                    soup = bs4.BeautifulSoup(content, features="lxml")
                    products_grid = soup.select('div[data-test="product-grid"] section>div')
                    print("products_grid find?=", len(products_grid))
                    # if not len(products_grid):
                    #     content = await page.content()
                    #     soup = bs4.BeautifulSoup(content, features="lxml")
                    #     products_grid = soup.select('div[data-test="product-grid"] section>div')
                    for item in products_grid[0].contents:
                        # print(item)
                        # print(item.text)
                        # print(item.a['href'])
                        # pro = item.select('a[data-test="product-title"]')[0]
                        try:
                            product_name = item.text
                            product_category = category_name
                            product_url = item.a['href']
                        except:
                            continue
                        product_url = TARGET_HOMEPAGE + product_url
                        products.append({
                            "category": product_category,
                            "name": product_name,
                            "url": product_url
                        })
                        cnt += 1
                        print("product=", cnt, {
                            "category": product_category,
                            "name": product_name,
                            "url": product_url
                        })
                    page_num += 1
                    print("page_num=", page_num)
                products_count.append({
                    "category": category_name,
                    "count": cnt
                })
                print("products_count in this subcategory=", {
                    "category": category_name,
                    "count": cnt
                })
                print("end - finding products in subcategories")
                # end - finding products in subcategories
            else:
                # start - finding sub-subcategories
                print("start - finding sub-subcategories in subcategory")
                components = soup.select('div[data-component-type="Browse - Manual"]')
                print("components find?=", len(components))
                if len(components):
                    for comp in components:
                        # soup = bs4.BeautifulSoup(str(comp), features="lxml")
                        # soup = bs4.BeautifulSoup(soup.select(
                        #    'div.children')[0], features="lxml")
                        try:
                            children = comp.select('div.children')[0].contents
                        except:
                            children = comp.select('ul')[0].contents
                        print("children_cnt=", len(children))
                        for subcategory in children:
                            try:
                                sub_subcategory_name = subcategory.a.text
                                sub_subcategory_url = subcategory.a['href']
                            except:
                                continue
                            if sub_subcategory_url.find("http") < 0:
                                sub_subcategory_url = TARGET_HOMEPAGE + sub_subcategory_url
                            sub_subcategories.append({
                                'parent': category_name,
                                'subcategory': subcategory_name,
                                'name': sub_subcategory_name,
                                'url': sub_subcategory_url
                            })
                            print("sub_subcategory=", {
                                'parent': category_name,
                                'subcategory': subcategory_name,
                                'name': sub_subcategory_name,
                                'url': sub_subcategory_url
                            })
                print("end - finding sub-subcategories in this subcategory")
                # end - finding sub-subcategories
    print("sub_subcategories=", sub_subcategories)
    jsonString = json.dumps(sub_subcategories)
    jsonFile = open("sub-subcategories.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()
    print("end - finding in subcategories")
    # end - finding sub-subcategories or products list in subcategories
    if len(sub_subcategories):
        print("sub_subcategories not empty")

    # start - get information from products url
    if len(products):
        jsonString = json.dumps(products)
        jsonFile = open("products_url.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    # end - get information from products url
    # products_url = json.load(open(os.path.join("products_url.json")))
    # print("products_url=", products_url)
    products_url = products
    products = []
    for item in products_url:
        product_category = item['category']
        # product_name = item['name']
        target_url = item['url']
        # await page.goto(TARGET_HOMEPAGE + target_url)
        # await asyncio.sleep(5)
        # content = await page.content()
        # soup = bs4.BeautifulSoup(content, features="lxml")
        print("def get_price_name(target_url): " + target_url)
        product_name = 'Not Found'
        product_price = 'Not Found'
        product_description = 'Not Found'
        # product_category = 'Not Found'
        product_upc = 'Not Found'
        product_imageurl = 'Not Found'
        if not target_url:
            print("not target_url")
            # return {"upc": product_upc,
            #         "product_name": product_name,
            #         "product_price": product_price.replace('$', ''),
            #         "product_image": product_imageurl,
            #         "product_description": product_description,
            #         "product_category": product_category
            #         }
        else:
            await page.goto(target_url)
            await asyncio.sleep(5)
            content = await page.content()
            soup = bs4.BeautifulSoup(content, features="lxml")
            if len(soup.select('div[data-test="productNotFound"]')):
                products.append({"product_upc": product_upc,
                                 "product_url": target_url,
                                 "product_name": product_name,
                                 "product_price": product_price.replace('$', ''),
                                 "product_image": product_imageurl,
                                 "product_description": product_description,
                                 "product_category": product_category
                                 })

                # return {"upc": product_upc,
                #         "product_name": product_name,
                #         "product_price": product_price.replace('$', ''),
                #         "product_image": product_imageurl,
                #         "product_description": product_description,
                #         "product_category": product_category
                #         }
            else:
                price = soup.select('span[data-test="product-random-weight-price"]')
                # print(price)
                if not len(price):
                    await asyncio.sleep(5)
                    content = await page.content()
                    soup = bs4.BeautifulSoup(content, features="lxml")
                    price = soup.select('span[data-test="product-random-weight-price"]')
                if not len(price):
                    products.append({"product_upc": product_upc,
                                     "product_url": target_url,
                                     "product_name": product_name,
                                     "product_price": product_price.replace('$', ''),
                                     "product_image": product_imageurl,
                                     "product_description": product_description,
                                     "product_category": product_category
                                     })
                else:
                    product_price = price[0].text
                    print(product_price)
                    product_name = soup.select('h1[data-test="product-title"] span')[0].text
                    print(product_name)
                    product_upc = soup.find_all("b", string="UPC")[
                        0].parent.text.split(' ')[1]
                    print(product_upc)
                    product_imageurl = soup.select('button[data-test="product-carousel-item-0"] img')[0]['src']
                    print(product_imageurl)
                    # product_category = soup.select('.PWWrr:nth-child(2) > span > a > span')[0].text
                    # print(product_category)
                    product_description = soup.find_all("h3", string="Description")[
                        0].parent.div.text
                    print(product_description)
                    products.append({"product_upc": product_upc,
                                     "product_url": target_url,
                                     "product_name": product_name,
                                     "product_price": product_price.replace('$', ''),
                                     "product_image": product_imageurl,
                                     "product_description": product_description,
                                     "product_category": product_category
                                     })
        print("product=", {"product_upc": product_upc,
                           "product_url": target_url,
                           "product_name": product_name,
                           "product_price": product_price.replace('$', ''),
                           "product_image": product_imageurl,
                           "product_description": product_description,
                           "product_category": product_category
                           })
    await browser.close()
    # end - get all information of all products from target.com
    # insert new product and update old products in database
    for product in products:
        product_upc = product["product_upc"]
        product_url = product["product_url"]
        product_name = product["product_name"]
        product_price = float(product["product_price"])
        product_imageurl = product["product_image"]
        product_description = product["product_description"]
        product_category = product["product_category"]
        if product_upc == 'Not Found':
            # current product is unavailable
            sql_query = "SELECT * FROM products WHERE url=" + "'" + product_url + "'"
            if len(cur.execute(sql_query).fetchall()):
                # it is existed in database
                sql_query = "UPDATE products SET " + \
                    "update_date=" + "'" + today + "', " +  \
                    "close_date=" + "'" + today + "', " +  \
                    "is_available=0" + ", " +  \
                    " WHERE url=" + "'" + product_url + "'"
                print(sql_query)
                cur.execute(sql_query)
                conn.commit()
            else:
                # it is not existed in database
                sql_query = "INSERT INTO products " + \
                            " (url, upc, name, description, image, price, category, open_date, update_date, close_cate, is_available) VALUES (" + \
                            "'" + product_url + "', " + \
                            '"' + product_upc + '", ' + \
                            '"' + product_name + '", ' + \
                            '"' + product_description + '", ' + \
                            "'" + product_imageurl + "', " + \
                            str(product_price) + ", " + \
                            '"' + product_category + '", ' + \
                            '"' + today + '", ' + \
                            '"' + today + '", ' + \
                            '"' + today + '", ' + \
                            '0);'
                print(sql_query)
                cur.execute(sql_query)
                conn.commit()
        else:
            # current product is available
            sql_query = "SELECT * FROM products WHERE upc=" + "'" + product_upc + "'"
            if len(cur.execute(sql_query).fetchall()):
                # it is existed in database
                sql_query = "UPDATE products SET " + \
                            "name=" + "'" + product_name + "'" + ", " + \
                            "description=" + "'" + product_description + "'" + ", " + \
                            "image=" + "'" + product_imageurl + "', " +  \
                            "category=" + "'" + product_category + "', " +  \
                            "price=" + str(product_price) + ", " +  \
                            "update_date=" + "'" + today + "', " +  \
                            " WHERE upc=" + "'" + product_upc + "'"
                print(sql_query)
                cur.execute(sql_query)
                conn.commit()
            else:
                # it is not existed in database = new data
                sql_query = "INSERT INTO products " + \
                            " (url, upc, name, description, image, price, category, open_date, update_date) VALUES (" + \
                            "'" + product_url + "', " + \
                            '"' + product_upc + '", ' + \
                            '"' + product_name + '", ' + \
                            '"' + product_description + '", ' + \
                            "'" + product_imageurl + "', " + \
                            str(product_price) + ", " + \
                            '"' + product_category + '", ' + \
                            '"' + today + '", ' + \
                            '"' + today + '"' + \
                            ');'
                print(sql_query)
                cur.execute(sql_query)
                conn.commit()

    conn.close()


async def get_price_name(target_url):
    print("def get_price_name(target_url): " + target_url)
    product_name = 'Not Found'
    product_price = 'Not Found'
    product_description = 'Not Found'
    product_category = 'Not Found'
    product_upc = 'Not Found'
    product_imageurl = 'Not Found'
    if not target_url:
        return {"upc": product_upc,
                "product_name": product_name,
                "product_price": product_price.replace('$', ''),
                "product_image": product_imageurl,
                "product_description": product_description,
                "product_category": product_category
                }
    browser = await pyppeteer.launch(handleSIGINT=False,
                                     handleSIGTERM=False,
                                     handleSIGHUP=False)
    page = await browser.newPage()
    await page.goto(target_url)
    await asyncio.sleep(5)
    content = await page.content()
    soup = bs4.BeautifulSoup(content, features="lxml")
    if len(soup.select('div[data-test="productNotFound"]')):
        await browser.close()
        return {"upc": product_upc,
                "product_name": product_name,
                "product_price": product_price.replace('$', ''),
                "product_image": product_imageurl,
                "product_description": product_description,
                "product_category": product_category
                }
    price = soup.select('span[data-test="product-random-weight-price"]')
    # print(price)
    while not len(price):
        content = await page.content()
        soup = bs4.BeautifulSoup(content, features="lxml")
        if len(soup.select('div[data-test="productNotFound"]')):
            await browser.close()
            return {"upc": product_upc,
                    "product_name": product_name,
                    "product_price": product_price.replace('$', ''),
                    "product_image": product_imageurl,
                    "product_description": product_description,
                    "product_category": product_category
                    }
        price = soup.select('span[data-test="product-random-weight-price"]')
        # print(price)
        if len(price):
            product_price = price[0].text
            print(product_price)
        await asyncio.sleep(1)
    product_name = soup.select('h1[data-test="product-title"] span')[0].text
    print(product_name)
    product_upc = soup.find_all("b", string="UPC")[0].parent.text.split(' ')[1]
    print(product_upc)
    product_imageurl = soup.select(
        'button[data-test="product-carousel-item-0"] img')[0]['src']
    print(product_imageurl)
    product_category = soup.select(
        '.PWWrr:nth-child(2) > span > a > span')[0].text
    print(product_category)
    product_description = soup.find_all("h3", string="Description")[
        0].parent.div.text
    print(product_description)
    await browser.close()
    return {"upc": product_upc,
            "product_name": product_name,
            "product_price": product_price.replace('$', ''),
            "product_image": product_imageurl,
            "product_description": product_description,
            "product_category": product_category
            }


async def get_target(upc_number):
    print("def get_target(upc_number): " + upc_number)
    product_name = 'Not Found'
    product_price = 'Not Found'
    product_description = 'Not Found'
    product_category = 'Not Found'
    product_upc = upc_number
    product_imageurl = 'Not Found'
    browser = await pyppeteer.launch(
                                     headless = False,
                                     executablePath="C:/Program Files/Google/Chrome/Application/chrome.exe",
                                     handleSIGINT=False,
                                     handleSIGTERM=False,
                                     handleSIGHUP=False)
    page = await browser.newPage()
    await page.goto("https://www.target.com/s?searchTerm=" + upc_number)
    content = await page.content()
    soup = bs4.BeautifulSoup(content, features="lxml")
    results = soup.select('h2[data-test="resultsHeading"]')
    while not len(results):
        content = await page.content()
        soup = bs4.BeautifulSoup(content, features="lxml")
        results = soup.select('h2[data-test="resultsHeading"]')
    res_num = int(results[0].text.split(' ')[0])
    # print(res_num)
    if not res_num:
        target_url = ""
    else:
        target_url = "https://www.target.com" + soup.select('section a')[0].get('href')
    if not target_url:
        return {"upc": product_upc,
                "product_name": product_name,
                "product_price": product_price.replace('$', ''),
                "product_image": product_imageurl,
                "product_description": product_description,
                "product_category": product_category
                }
    print(target_url)
    await page.goto(target_url)
    content = await page.content()
    soup = bs4.BeautifulSoup(content, features="lxml")
    # price = soup.select('span[data-test="product-random-weight-price"]')
    price = soup.select('span[data-test="product-price"]')
    print(price)
    try:
        print(price[0])
        product_price = price[0].text
        print(product_price)
    except:
        pass
    while not len(price):
        content = await page.content()
        soup = bs4.BeautifulSoup(content, features="lxml")
        price = soup.select('span[data-test="product-price"]')
        print(price)
        try:
            print(price[0])
            product_price = price[0].text
            print(product_price)
        except:
            pass
        # await asyncio.sleep(1)
    product_name = soup.select('h1[data-test="product-title"] span')[0].text
    print(product_name)
    # product_upc = soup.find_all("b", string="UPC")[0].parent.text.split(' ')[1]
    # print(product_upc)
    product_imageurl = soup.select('button[data-test="product-carousel-item-0"] img')[0]['src']
    print(product_imageurl)
    product_category = soup.select('.PWWrr:nth-child(2) > span > a > span')[0].text
    print(product_category)
    product_description = soup.find_all("h3", string="Description")[0].parent.div.text
    print(product_description)
    await browser.close()
    return {"upc": product_upc,
            "product_name": product_name,
            "product_price": product_price.replace('$', ''),
            "product_image": product_imageurl,
            "product_description": product_description,
            "product_category": product_category
            }
        
    
async def get_price_name(target_url):
    print("def get_price_name(target_url): " + target_url)
    product_name = 'Not Found'
    product_price = 'Not Found'
    product_description = 'Not Found'
    product_category = 'Not Found'
    product_upc = 'Not Found'
    product_imageurl = 'Not Found'
    if not target_url:
        return {"upc": product_upc,
                "product_name": product_name,
                "product_price": product_price.replace('$', ''),
                "product_image": product_imageurl,
                "product_description": product_description,
                "product_category": product_category
                }
    browser = await pyppeteer.launch(handleSIGINT=False,
                                     handleSIGTERM=False,
                                     handleSIGHUP=False)
    page = await browser.newPage()
    await page.goto(target_url)
    content = await page.content()
    soup = bs4.BeautifulSoup(content, features="lxml")
    price = soup.select('span[data-test="product-random-weight-price"]')
    # print(price)
    while not len(price):
        content = await page.content()
        soup = bs4.BeautifulSoup(content, features="lxml")
        price = soup.select('span[data-test="product-random-weight-price"]')
        # print(price)
        if len(price):
            product_price = price[0].string
            print(product_price)
        await asyncio.sleep(1)
    product_name = soup.select('h1[data-test="product-title"] span')[0].text
    print(product_name)
    product_upc = soup.find_all("b", string="UPC")[0].parent.text.split(' ')[1]
    print(product_upc)
    product_imageurl = soup.select('button[data-test="product-carousel-item-0"] img')[0]['src']
    print(product_imageurl)
    product_category = soup.select('.PWWrr:nth-child(2) > span > a > span')[0].text
    print(product_category)
    product_description = soup.find_all("h3", string="Description")[0].parent.div.string
    print(product_description)
    await browser.close()
    return {"upc": product_upc,
            "product_name": product_name,
            "product_price": product_price.replace('$', ''),
            "product_image": product_imageurl,
            "product_description": product_description,
            "product_category": product_category
            }
    
async def scrap_all_products(target_url):
    print("def get_price_name(target_url): " + target_url)
    product_upc = 'Not Found'
    product_name = 'Not Found'
    product_description = 'Not Found'
    product_imageurl = 'Not Found'
    product_category = 'Not Found'
    product_price = 'Not Found'
    product_price = 'Not Found'
    
    browser = await pyppeteer.launch()
    page = await browser.newPage()
    await page.goto(target_url)
    content = await page.content()
    soup = bs4.BeautifulSoup(content, features="lxml")
    price = soup.select('span[data-test="product-random-weight-price"]')
    print(price)
    while not len(price):
        content = await page.content()
        soup = bs4.BeautifulSoup(content, features="lxml")
        price = soup.select('span[data-test="product-random-weight-price"]')
        print(price)
        if len(price):
            product_price = price[0].string
            print(product_price)
        await asyncio.sleep(1)
    product_name = soup.select('h1[data-test="product-title"] span')[0].text
    print(product_name)
    product_upc = soup.find_all("b", string="UPC")[0].parent.text.split(' ')[1]
    print(product_upc)
    product_imageurl = soup.select(
        'button[data-test="product-carousel-item-0"] img')[0]['src']
    print(product_imageurl)
    product_category = soup.select('.PWWrr:nth-child(2) > span > a > span')[0].text
    print(product_category)
    product_description = soup.find_all("h3", string="Description")[0].parent.div.string
    print(product_description)
    await browser.close()
    return {"upc": product_upc,
            "product_name": product_name,
            "product_price": product_price.replace('$', ''),
            "product_image": product_imageurl,
            "product_description": product_description,
            "product_category": product_category
            }
    
# def get_price_name(target_url): 
    # print("def get_price_name(target_url): " + target_url)
    # product_name = 'Not Found'
    # product_price = 'Not Found'
    # product_description = 'Not Found'
    # product_category = 'Not Found'
    # product_upc = 'Not Found'
    # product_imageurl = 'Not Found'
    
    # try:
    #     driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    #     driver.get(target_url)
    #     WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//h1[@data-test = 'product-title']/span")))
    #     print("PAGE IS READY = " + target_url)
    # except TimeoutException:
    #     print("Loading took too much time!")

    # try:
    #     product_name = driver.find_element(By.XPATH, "//h1[@data-test = 'product-title']/span").text
    # except NoSuchElementException as e:
    #     product_name = 'Not Found'

    # # print("Product Name = " + product_name)

    # try:      
    #     product_description = driver.find_element(By.XPATH, "//h3[text() = 'Description']/parent::div/div[1]").get_attribute("innerText")
    # except NoSuchElementException as e:
    #     product_description = 'Not Found'

    # # print("Product Description = " + product_description)

    # try:
    #     print("first price try")   
    #     time.sleep(2)   
    #     product_price = driver.find_element(By.XPATH, "//div[@data-test = 'product-price']").text
    #     print("Product Price =- " + product_price)
    # except NoSuchElementException as e:
    #     product_price = 'Not Found'

    # if product_price == 'Not Found':
    #     print("second price try")    
    #     time.sleep(2)    
    #     try:      
    #         product_price = driver.find_element(By.CSS_SELECTOR, ".kfATIS").text
    #         print("Product Price =% " + product_price)
    #     except NoSuchElementException as e:
    #         product_price = 'Not Found'

    # if product_price == 'Not Found' or product_price=='See price in cart':
    #     try:      
    #         ship_button = driver.find_element(By.XPATH, "//button[@data-test = 'shipItButton']")
    #         ship_button.click()
    #         try:
    #             WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//button[@data-test = 'espModalContent-declineCoverageButton']")))
    #             decline_coverage_button = driver.find_element(By.XPATH, "//button[@data-test = 'espModalContent-declineCoverageButton']")
    #             decline_coverage_button.click()
    #         except Exception as e2:
    #             pass
    #         WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//p[@data-test = 'addToCartModalPrice']/span")))
    #         product_price = driver.find_element(By.XPATH, "//p[@data-test = 'addToCartModalPrice']/span").get_attribute("innerText")
    #     except Exception as e:
    #         product_price = 'Not Found'

    # print("Product Price =+= " + product_price)

    # # print("Product Price = " + product_price)

    # try:      
    #     product_category = driver.find_element(By.CSS_SELECTOR, ".PWWrr:nth-child(2) span").text
    #     print("product_category =# " + product_category)
    # except NoSuchElementException as e:
    #     product_category = 'Not Found'

    # print("Product Category === " + product_category)

    # try:
    #     product_upc = driver.find_element(By.XPATH, "//h3[text() = 'Specifications']/parent::div//b[text() = 'UPC']/parent::div").get_attribute('innerText')
    #     product_upc = product_upc.replace("UPC:", "");
    #     product_upc = product_upc.strip()
    # except NoSuchElementException as e:
    #     product_upc = 'Not Found'

    # # print("Product UPC = " + product_upc)

    # try:      
    #     product_imageurl = driver.find_element(By.XPATH, "//div[@class = 'slide--active']//div[@class = 'slideDeckPicture']//img").get_attribute('src') 
    #     # product_image_name= 'Test1.png'
    #     # urllib.request.urlretrieve(product_imageurl, "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png")   
    # except NoSuchElementException as e:
    #     product_imageurl = 'https://origamiitlab.com/wp-content/uploads/2018/12/bird.png'
    #     # product_image_name= 'Test_default.png'

    # # print("Product Image URL = " + product_imageurl)

    # driver.close()
    # driver.quit()
    
    
    # return asyncio.run(scrap_upc_details(target_url))

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    try:
        jsonFetched = res['items']
    except:
        return 0
    
    return res['items']

# This code is not working anymore as redsky api is not functional
def gget_price_name_NOT_USED(upc, stock, disc, employee): 
    print("# This code is not working anymore as redsky api is not functional")
    url = 'https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v1'

    payload = {
    "key": "ff457966e64d5e877fdbad070f276d18ecec4a01",
    "channel": "WEB",
    "count": "24",
    "default_purchasability_filter": "false",
    "include_sponsored": "true",
    "keyword": upc,
    "offset": "0",
    "page": "/s/lego duplo",
    "platform": "desktop",
    "pricing_store_id": "3991",
    "useragent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "visitor_id": "AAA",}

    data =  requests.get(url, params=payload).json()    

    # uncomment this to print all data;
    #print(json.dumps(data, indent=4))

    # print some data to screen
    flag=False
    product_name = 'Not Found'
    product_price = 'Not Found'
    product_description = 'Not Found'
    product_category = 'Select'
    
    # Delete old file before downloading new one
    product_image_path= 'C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png'
    file = pathlib.Path(product_image_path)
    if file.exists():
        os.remove(product_image_path)
        

    try:
        product_name = (html.unescape(data['search_response']['items']['Item'][0]['title']))

        tcin = data['search_response']['items']['Item'][0]['representative_child_part_number']
        url_tcin = 'https://redsky.target.com/web/pdp_location/v1/tcin/%s' %tcin
        payload = {
        'pricing_store_id': '3991',
        'key': 'ff457966e64d5e877fdbad070f276d18ecec4a01'}
        jsonData = requests.get(url_tcin, params=payload).json()
        product_price = str(jsonData['price']['reg_retail'])
         
        product_description = str((data['search_response']['items']['Item'][0]['description']))
        
        product_category= str((data['search_response']['facet_list'][0]['details'][0]['display_name']))
        base_url = str((data['search_response']['items']['Item'][0]['images'][0]['base_url']))
        base_path = str((data['search_response']['items']['Item'][0]['images'][0]['primary']))
        product_image_url = base_url + base_path
        
        product_image_name= 'Test1.png'
        urllib.request.urlretrieve(product_image_url, "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png")
    except:
        product_image_name= 'Test_default.png'


    return {"upc":upc,
            "product_name":product_name,
            "product_price":product_price.replace('$', ''),
            "product_image" : product_image_name,
            "product_description" : product_description,
            "product_category": product_category
            }
        
        
    
# scraping by selenium
async def get_price_name_OLD(upc, stock, disc, employee): 
    print("# scraping by selenium")
    product_name = 'Not Found'
    product_price = 'Not Found'
    product_description = 'Not Found'
    product_category = 'Select'

    # Delete old file before downloading new one
    product_image_path= 'C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png'
    file = pathlib.Path(product_image_path)
    if file.exists():
        os.remove(product_image_path)

    config = json.load(open(config_url))
    my_api_key = config['GoogleAPI']
    my_cse_id = config['CSEID']

    results = google_search(upc, my_api_key, my_cse_id, num=1)
    if results==0:
        product_price=0
        return(upc + "|Not Found|0")
        
    for result in results:
        target_url=result['link']
    
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(target_url)
        myElem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//h1[@data-test = 'product-title']")))
        print("PAGE IS READY = " + target_url)
    except TimeoutException:
        print("Loading took too much time!")
    
    try:      
        product_name = driver.find_element(By.XPATH, "//h1[@data-test = 'product-title']").text
    except Exception as e:
        product_name = 'Not Found'

    try:      
        product_description = driver.find_element(By.XPATH, "//h3[text()='Description']//parent::div//div").text
    except Exception as e:
        product_description = 'Not Found'

    try:   
        product_category = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div/span[2]/span[1]/a/span").text
        print("product_category",product_category)
    except Exception as e:
        product_category = 'Select'

    try:      
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@data-test = 'product-price']")))
        product_price = driver.find_element(By.XPATH, "//div[@data-test = 'product-price']").text        
    except Exception as e:        
        product_price = 'Not Found'

    try:      
        image = driver.find_element(By.XPATH, "//div[@class='slideDeckPicture']//picture/img[1]")
        product_image_url = image.get_attribute('src')     
        print(product_image_url)
        product_image_name= 'Test1.png'
        urllib.request.urlretrieve(product_image_url, "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png")   
    except Exception as e:        
        product_image_name= 'Test_default.png'
        
    driver.quit() 
    

    return {"upc":upc,
            "product_name":product_name,
            "product_price":product_price.replace('$', ''),
            "product_image" : product_image_name,
            "product_description" : product_description,
            "product_category": product_category
            }

# This code is not used anymore as we are using direct link instead of Google search UPC
async def get_price_name_OLD_OLD(upc, stock, disc, employee): 
    print("# This code is not used anymore as we are using direct link instead of Google search UPC")
    product_name = 'Not Found'
    product_price = 'Not Found'
    product_description = 'Not Found'
    product_category = 'Select'

    # Delete old file before downloading new one
    product_image_path= 'C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png'
    file = pathlib.Path(product_image_path)
    if file.exists():
        os.remove(product_image_path)

    config = json.load(open(config_url))
    my_api_key = config['GoogleAPI']
    my_cse_id = config['CSEID']

    results = google_search(upc, my_api_key, my_cse_id, num=1)
    if results==0:
        product_price=0
        return(upc + "|Not Found|0")
        
    for result in results:
        target_url=result['link']
    
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(target_url)
        myElem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//h1[@data-test = 'product-title']")))
        print("PAGE IS READY = " + target_url)
    except TimeoutException:
        print("Loading took too much time!")
    
    try:      
        product_name = driver.find_element(By.XPATH, "//h1[@data-test = 'product-title']").text
    except Exception as e:
        product_name = 'Not Found'

    try:      
        product_description = driver.find_element(By.XPATH, "//h3[text()='Description']//parent::div//div").text
    except Exception as e:
        product_description = 'Not Found'

    try:   
        product_category = driver.find_element(By.XPATH, "//div[@data-test='breadcrumb']//span[2]//span[@itemprop='name']").text
    except Exception as e:
        product_category = 'Select'

    try:      
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@data-test = 'product-price']")))
        product_price = driver.find_element(By.XPATH, "//div[@data-test = 'product-price']").text        
    except Exception as e:        
        product_price = 'Not Found'

    try:      
        image = driver.find_element(By.XPATH, "//div[@class='slideDeckPicture']//picture/img[1]")
        product_image_url = image.get_attribute('src')     
        print(product_image_url)
        product_image_name= 'Test1.png'
        urllib.request.urlretrieve(product_image_url, "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png")   
    except Exception as e:        
        product_image_name= 'Test_default.png'
        
    driver.quit() 
    

    return {"upc":upc,
            "product_name":product_name,
            "product_price":product_price.replace('$', ''),
            "product_image" : product_image_name,
            "product_description" : product_description,
            "product_category": product_category
            }
    

   


def gget_price_name(upc, stock, disc, employee): 
    print("def gget_price_name(upc, stock, disc, employee): ")
    url = 'https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v1'

    payload = {
    "key": "ff457966e64d5e877fdbad070f276d18ecec4a01",
    "channel": "WEB",
    "count": "24",
    "default_purchasability_filter": "false",
    "include_sponsored": "true",
    "keyword": upc,
    "offset": "0",
    "page": "/s/lego duplo",
    "platform": "desktop",
    "pricing_store_id": "3991",
    "useragent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "visitor_id": "AAA",}

    data =  requests.get(url, params=payload).json()    

    # uncomment this to print all data;
    #print(json.dumps(data, indent=4))

    # print some data to screen
    flag=False
    product_name = 'Not Found'
    product_price = 'Not Found'
    product_description = 'Not Found'
    product_category = 'Select'
    
    # Delete old file before downloading new one
    product_image_path= 'C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png'
    file = pathlib.Path(product_image_path)
    if file.exists():
        os.remove(product_image_path)
        

    try:
        product_name = (html.unescape(data['data']['search']['products'][0]['item']['product_description']['title']))
        product_price = str(data['data']['search']['products'][0]['price']['current_retail'])
         
        # upc = str((data['data']['search']['search_response']['typed_metadata']['keyword']))
        
        product_category= str((data['data']['search']['search_response']['facet_list'][0]['details'][0]['display_name']))
        product_image_url = str((data['data']['search']['products'][0]['item']['enrichment']['images']['primary_image_url']))
                
        product_image_name= 'Test1.png'
        urllib.request.urlretrieve(product_image_url, "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png")
    except:
        product_image_name= 'Test_default.png'


    return {"upc":upc,
            "product_name":product_name,
            "product_price":product_price.replace('$', ''),
            "product_image" : product_image_name,
            "product_description" : product_description,
            "product_category": product_category
            }
        
        




async def get_walamart_price(upc):
    
    price = 0
    
    url = 'https://search.mobile.walmart.com/v1/products-by-code/UPC/' + upc + '?storeId=1'
    
    headers = { 'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding':'gzip, deflate, br',
    'accept-language':'en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7',
    'cache-control':'max-age=0',
    'upgrade-insecure-requests':'1',
    'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
    }

    try:
        data =  requests.get(url, headers=headers).json()
    except:
        price=0
        name = 'Not Found'
        product_image_name= 'Test_default.png'




    try:
        price =int(data['data']['online']['price']['priceInCents'])/100
        name =data['data']['common']['name']
        
        product_image_url = str(data['data']['common']['productImageUrl'])
        
        product_image_name= 'Test1.png'
        urllib.request.urlretrieve(product_image_url, "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png")

    except:
        price=0
        name = 'Not Found'
        product_image_name= 'Test_default.png'
    
    return {"upc":upc,
            "product_name":name,
            "product_image" : product_image_name,
            "product_price":str(price),
            "product_description" : name,
            "product_category": 'Select'
            }



def gget_amazon_price(upc, stock, disc, employee): 

    results = google_search(upc, my_api_key, my_cse_id, num=1)
    if results==0:
        product_price=0
        return(upc + "|Not Found|0")
        
    for result in results:
        target_url=result['link']
    
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(target_url)
        myElem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//h1[@data-test = 'product-title']")))
        print("PAGE IS READY")
    except TimeoutException:
        print("Loading took too much time!")
    
    try:      
        product_name = driver.find_element(By.XPATH, "//h1[@data-test = 'product-title']").text
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@data-test = 'product-price']")))
        product_price = driver.find_element(By.XPATH, "//div[@data-test = 'product-price']").text
    except Exception as e:
        product_name = 'Not Found'
        product_price = 'Not Found'

    driver.quit() 
    
    return {"upc":upc,
            "product_name":product_name,
            "product_price":product_price
            }
    


async def get_amazon_price(upc):
    url = 'https://www.googleapis.com/customsearch/v1/siterestrict?key=AIzaSyABrORAknu9lQMCLqvdTTyGiAmamOo21SY&cx=cb360a9b4d70671b4&q=' + upc + '&fields=items(link)'

    data =  requests.get(url).json()
    if len(data)==0:
        return  {'price': '$00.00'}
    else:
        for i in data['items']:
            amazon_url = i['link']
            break

        return scrape(amazon_url)


def get_amazon_price_by_link(link):
    return scrape(link)

def scrape(url):  
    # print(url)
    yaml_string = """
    name:
        css: '#productTitle'
        type: Text
    
    price:
        css: 'span.a-price.a-text-price.a-size-medium.apexPriceToPay'
        type: Text
        children:
            withdeal: 
                css: span.a-offscreen
                type: Text

    deal:
        css: '#priceblock_dealprice'
        type: Text

    sale:
        css: '#priceblock_saleprice'
        type: Text

    image:
        css: '#landingImage'
        type: Image
        attribute: src

    """
    e = Extractor.from_yaml_string(yaml_string)

    text = ''
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(url)
        text = driver.page_source
    except TimeoutException:
        print("Loading took too much time!")

    return e.extract(text)

    # headers = {
    #     'dnt': '1',
    #     'upgrade-insecure-requests': '1',
    #     'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    #     'sec-fetch-site': 'same-origin',
    #     'sec-fetch-mode': 'navigate',
    #     'sec-fetch-user': '?1',
    #     'sec-fetch-dest': 'document',
    #     'referer': 'https://www.amazon.com/',
    #     'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    # }

    

    # Download the page using requests
    #print("Downloading %s"%url)
    # r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    # if r.status_code > 500:
    #     if "To discuss automated access to Amazon data please contact" in r.text:
    #         print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
    #     else:
    #         print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
    #     return None
    # Pass the HTML of the page and create 
    # return e.extract(r.text)
