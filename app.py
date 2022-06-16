from flask import Flask, render_template, request, redirect
from werkzeug.datastructures import Range
from sheets import update_details
from scraper import get_amazon_price_by_link, get_price_name, get_walamart_price, get_amazon_price
from squares import add_to_square
from marketplace import uploadToMP, publish
from printzpls import printlabel, open_acrobat_print
from openpyxl import load_workbook
from ig import postInstagram

import time
import os
import pandas as pd

import datetime
import json
import asyncio
import urllib.request

import csv
import time
timestr = time.strftime("%Y%m%d")


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "static/data", "categories.json")
config_url = os.path.join(SITE_ROOT, "static/data", "config.json")
data_date_url = os.path.join(SITE_ROOT, "static/data", "data" + timestr + ".json")
data_url = os.path.join(SITE_ROOT, "static/data", "data.json")
data_ig_url = os.path.join(SITE_ROOT, "static/data", "data_ig.json")

upcDetails=""


app = Flask(__name__)
     

@app.route('/add', methods = ['GET', 'POST'])
def add_produtcs():
    if request.method == "POST":
        try:
            stock=request.form["Stock"]
        except:
            stock=0
        
        try:
            printlabels = int(request.form["printlabels"])
        except:
            printlabels = 1
            
        employee=request.form["VendorName"]  
        
        if request.form["btn"] == 'Print New Label':
            product_name = request.form["Name"]  
            product_price = '$'+request.form["Price"]  
            description = request.form["Description"] 
            #category = request.form["Category"] 
            category = "Miscellaneous"
            condition = request.form["Condition"]             
            upc = datetime.datetime.now().strftime('%Y%m%d%H%M')
            stock = request.form["Stock"] 
            imgpath = request.files["filename"].filename
            
            try:
                addFBListing = request.form["addFBListing"]
            except:
                addFBListing = 'off'
                
            if(addFBListing=='on'):
                link_to_mp_post = uploadToMP(product_name, product_price, description, upc, category, condition, imgpath)
                

            add_to_square(product_name, upc, str(product_price) + "00", employee, stock)
            print('Posted to Square')

            itemCounter = update_details(upc, product_name, product_price, stock, "0", employee, link_to_mp_post['link'], link_to_mp_post['imglink'], description)
            print('Posted to Catalog')

            count = itemCounter["count"]
            zpl = printlabel(upc, product_name, product_price, "0")
            
            if "." in request.form["Price"]:
                add_to_square(product_name, upc, request.form["Price"], employee, stock)
            else:
                add_to_square(product_name, upc, request.form["Price"] + "00", employee, stock)
            
            imgname = open_acrobat_print(printlabels)
            
            return render_template('add.html', count=count, zpl=zpl, label=imgname, upc=upc)
            
        
        
        
    return render_template('add.html', count=0, zpl="", label="", upc="")  
    
@app.route('/updateDiscount', methods = ['GET', 'POST'])
def updateDiscount():
    if(request.method=='POST'):
        
        value = request.form['discounts']
        pk = request.form['pk']
        
        categories = json.load(open(json_url))
        categories[pk]=value
        
        print(categories)
        # Serializing json 
        json_object = json.dumps(categories, indent = 4)
        
        # Writing to sample.json
        with open(json_url, "w") as outfile:
            outfile.write(json_object)

        return render_template('configuration.html', categories=categories)     

@app.route('/configuration', methods = ['GET', 'POST'])            
def configuration():
    
    categories = json.load(open(json_url))
    config = json.load(open(config_url))
    
    if(request.method=='POST'):
        
        config['Images Count'] = request.form['ImagesCount']
        config['Cover Image Path'] = request.form['CoverImagePath']
        config['Schedule'] = request.form['Schedule']
        config['Delay'] = request.form['Delay']
        config['CSEID'] = request.form['CSEID']
        config['GoogleAPI'] = request.form['GoogleAPI']
        config['InstaPrice'] = request.form['InstaPrice']
        
        print(config)
        # Serializing json 
        json_object = json.dumps(config, indent = 4)
        
        # Writing to sample.json
        with open(config_url, "w") as outfile:
            outfile.write(json_object)

        return render_template('configuration.html', categories=categories, config=config)     

    return render_template('configuration.html', categories=categories, config=config)     
    

@app.route('/old', methods = ['GET', 'POST'])
def homepage():
    
    global upcDetails
    
    if request.method == "POST":
        upc=request.form["upc"]
        try:
            stock=request.form["Stock"]
        except:
            stock=0
        try:
            disc=request.form["Discount"]  
        except:
            disc=0
        
        try:
            printlabels = int(request.form["printlabels"])
        except:
            printlabels = 1
             
        employee=request.form["VendorName"]   
        amazon_price =0 
        walmart_price = 0
        target_product_price=0
        
        

        
        if request.form["btn"] == 'Fetch Details':  
            # starting time
            start = time.time()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = get_price_name(upc, stock, disc, employee), get_walamart_price(upc)
            upcDetailsTarget, upcDetailsWalmart = loop.run_until_complete(asyncio.gather(*tasks))
            # tasks = get_price_name(upc, stock, disc, employee), get_walamart_price(upc), get_amazon_price(upc)
            # upcDetailsTarget, upcDetailsWalmart, upcDetailsAmazon = loop.run_until_complete(asyncio.gather(*tasks))
            print("get_price_name()={upcDetailsTarget}, get_walamart_price()={upcDetailsWalmart}".format(**vars()))
            loop.close()
            
            # upcDetails=get_price_name(upc, stock, disc, employee)   
            lowest_price = 0
            upcDetails = upcDetailsTarget
            try:                
                target_product_price = upcDetailsTarget["product_price"]
                lowest_price = float(target_product_price)
                upcDetails["lowest_price"] = lowest_price
            except:
                target_product_price = 0
                
            try:                
                walmart_price = upcDetailsWalmart["product_price"]
                if float(target_product_price) == 0:
                    lowest_price = float(walmart_price)
                    upcDetails["lowest_price"] = lowest_price
                elif float(walmart_price) > 0:
                    if float(float(target_product_price) - float(walmart_price)) > 0:
                        lowest_price = float(walmart_price)
                        upcDetails["lowest_price"] = lowest_price
            except:
                walmart_price = 0
            
            # try:                
            #     amazon_price = upcDetailsAmazon["price"].replace('$','')
            #     if float(lowest_price) == 0:
            #         lowest_price = float(amazon_price)
            #     elif float(amazon_price) > 0:
            #         if float(float(lowest_price) - float(amazon_price)) > 0:
            #             lowest_price = float(amazon_price)                
            # except:
            #     amazon_price = 0    
            
            if 'Not Found' in upcDetails["product_name"]:
                print('Not found in Target')
                # upcDetails = get_walamart_price(upc)
                upcDetails = upcDetailsWalmart
                walmart_price = upcDetails["product_price"]
                
                target_product_price="0"
                                

                # if 'Not Found' in upcDetails["product_name"]:
                #     print('Not found in Walmart')
                #     # data = get_amazon_price(upc)
                #     data = upcDetailsAmazon
                #     try:
                #         amazon_price = data['price']
                #         product_name = data['name']
                #     except:
                #         print('Not found in Amazon')
                #         amazon_price = 0
                #         product_name = 'NOT FOUND'
                        
                #     upcDetails = {
                #                 "upc":upc,
                #                 "product_name":product_name,
                #                 "product_price":lowest_price,
                #                 "product_image" : 'Test_default.png',
                #                 "product_description" : product_name,
                #                 "product_category": 'Select'
                #                 }
            #     else:
            #         amazon_price =0
            # else:
            #     walmart_price =0

             # end time
            end = time.time()
            
            runtime = end - start
            dur='%.2f' % runtime
            
                           
            for filename in os.listdir('static/'):
                if filename.startswith('label'):  # not to remove other images
                    imgname = filename
            
           
            categories = json.load(open(json_url))    
            categoryFoundFlag = 0
            discountPercent = 0
            for name, discount in categories.items():
                if name in upcDetails["product_category"]:  
                    categoryFoundFlag = 1   
                    discountPercent = discount
                       
            return render_template('home.html', 
                                   lowest_price = lowest_price,
                                   details=upcDetails, 
                                   duration=dur, 
                                   counter=0,  
                                   zpl="", 
                                   label=imgname, 
                                   target=target_product_price, 
                                   walmart=walmart_price, 
                                   amazon=amazon_price,
                                   categories=categories,
                                   categoryFoundFlag=categoryFoundFlag,
                                   discount = discountPercent)
            
        elif request.form["btn"] == 'Print Label':
            # starting time
            
            start = time.time()
            
            product_name = upcDetails["product_name"]
            product_price = upcDetails["lowest_price"]
            product_description = upcDetails["product_description"]
            product_category = upcDetails["product_category"]
            

            try:
                addFBListing = request.form["addFBListing"]
            except:
                addFBListing = 'off'


            try:
                imgpath = upcDetails["product_image"]
            except:
                imgpath="Test1.png"
                
            link_img_link={}
            link_img_link['link'] = 'https://origamiitlab.com/wp-content/uploads/2018/12/bird.png'
            link_img_link['imglink'] = 'https://origamiitlab.com/wp-content/uploads/2018/12/bird.png'

            try: 
                price1 = float(product_price.replace("$", ""))
            except:
                price1 = float(product_price)

            if disc=="" or disc=='0':
                discountedPrice=product_price
            else:    
                disc1=float(disc)
                discP = price1 - ((price1*disc1)/100)
                discountedPrice = '%.2f' % discP

            product_price1 =  round(float(discountedPrice))  
            
            if(addFBListing=='on'):
                              
                link_img_link = uploadToMP(product_name, product_price1, product_description, upc, "Miscellaneous", "New", imgpath)
                

            itemCounter = update_details(upc, 
                                         product_name, product_price, stock, disc, employee, link_img_link['link'], link_img_link['imglink'], product_description)
            
            count = itemCounter["count"]
            zpl = printlabel(upc, product_name, product_price, disc)

            add_to_square(product_name, upc, str(product_price) + "00", employee, stock)

            
            try:
                printlabels = int(request.form["printlabels"])
            except:
                printlabels = 1
            
            imgname = open_acrobat_print(printlabels)
            
            
            
            # end time
            end = time.time()
            
            runtime = end - start
            print('runtime')
            print(runtime)
            categories = json.load(open(json_url))
            categoryFoundFlag = 0
            discountPercent = 0
            for name, discount in categories.items():
                if name in upcDetails["product_category"]:  
                    categoryFoundFlag = 1
                    discountPercent = discount
                    
            default_details =   {"upc":upc,
                                    "product_name":product_name,
                                    "product_price":product_price,
                                    "product_category": product_category,
                                }
            return render_template('home.html', 
                                   details=default_details, 
                                   duration=runtime, 
                                   counter=count, 
                                   zpl=zpl, 
                                   label=imgname, 
                                   walmart=0, 
                                   amazon=0, 
                                   categories=categories,
                                   categoryFoundFlag=categoryFoundFlag,
                                   discount = discountPercent)
        
        
        else:
            print('Report bad parameter')
    else: 
        categories = json.load(open(json_url))   
        categoryFoundFlag = 0
        discountPercent = 0
        
        default_details = {"upc":"",
                       "product_name":"Title",
                       "product_price":"$0",
                       "product_category": "Select"
                    }
        
        for name, discount in categories.items():
            if name in default_details["product_category"]:  
                categoryFoundFlag = 1
                discountPercent = discount
                
        
        return render_template('home.html', 
                               details=default_details,
                               duration=0,counter=0,
                               walmart=0,
                               amazon=0,
                               categories=categories,
                               categoryFoundFlag=categoryFoundFlag,
                               discount=discountPercent)



@app.route('/add_to_marketplace', methods = ['GET', 'POST'])
def add_to_marketplace():
    
    config = json.load(open(config_url))
    delay = int(config['Delay'])
    delayInMin = int(delay * 60)

    if request.method == "POST":

        if request.form["btn"] == 'Publish':
            product_name = request.form["Name"]  
            product_price = '$'+request.form["Price"]  
            description = request.form["Description"] 
            category = "Miscellaneous"
            condition = "New"         
            upc = datetime.datetime.now().strftime('%Y%m%d%H%M')
            CoverImagePath = request.form["CoverImagePath"]
            ImageCount = config["Images Count"]
            
            path, dirs, files = next(os.walk(CoverImagePath))
            file_count = len(files)
            
            for i in range(int(int(file_count)/int(ImageCount))):
                publish(product_name, product_price, description, upc, category, condition, CoverImagePath, ImageCount)
                time.sleep(delayInMin)     
            
            return render_template('addtomarketplace.html', config=config)
 
    return render_template('addtomarketplace.html', config=config)  
    
@app.route('/amazon', methods = ['GET', 'POST'])
def amazon():
    
    global upcDetailsAmazon

    config = json.load(open(config_url))
    InstaPrice = int(config['InstaPrice'])
    
    if request.method == "POST":
        
        try:
            stock=request.form["Stock"]
        except:
            stock=0
        try:
            disc=request.form["Discount"]  
        except:
            disc=0
        
        try:
            printlabels = int(request.form["printlabels"])
        except:
            printlabels = 1
             
        employee=request.form["VendorName"]   
        amazon_price = 0 
        amazon_link = request.form["AmazonLink"]
        
        data = get_amazon_price_by_link(amazon_link)
        
        try:            
            product_image_url = str(data['image'])        
            urllib.request.urlretrieve(product_image_url, "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png")
            product_image_name= 'Test1.png'
        except:
            product_image_name= 'Test_default.png'


        if data['price']['withdeal'] is not None:
            amazon_price = data['price']['withdeal']                  
        elif data['deal'] is not None:
            amazon_price = data['deal']  
        elif data['sale'] is not None:
            amazon_price = data['sale']                    
        else:
            print('Not found in Amazon')
            amazon_price = 0

        # try:
        #     amazon_price = data['deal']
        # except:
        #     print('Not found in Amazon')
        #     amazon_price = data['price']

        try:
            # amazon_price = data['price']
            lowest_price = amazon_price
            product_name = data['name']
        except:
            print('Not found in Amazon')
            amazon_price = 0
            lowest_price = amazon_price
            product_name = 'NOT FOUND'
            
        upcDetailsAmazon = {
                    "product_name":product_name,
                    "product_price":amazon_price,
                    "product_image" : product_image_name,
                    "product_description" : product_name,
                    "product_category": 'Select'
                    }
        
        if request.form["btn"] == 'Fetch Details':  
            # starting time
            start = time.time()
            
             
            for filename in os.listdir('static/'):
                if filename.startswith('label'):  # not to remove other images
                    imgname = filename
            
           
            categories = json.load(open(json_url))    
            categoryFoundFlag = 0
            discountPercent = 0


            end = time.time()
            
            runtime = end - start
            dur = '%.2f' % runtime
                       
            return render_template('amazon.html', 
                                   lowest_price = lowest_price,
                                   details=upcDetailsAmazon, 
                                   duration=dur, 
                                   counter=0,  
                                   zpl='', 
                                   label=imgname, 
                                   amazon=amazon_price,
                                   categories=categories,
                                   categoryFoundFlag=categoryFoundFlag,
                                   discount = discountPercent)
            
            
            
            
        elif request.form["btn"] == 'Print Label':
            # starting time
            
            start = time.time()
                        
            upc = datetime.datetime.now().strftime('%Y%m%d%H%M')
            product_name = upcDetailsAmazon["product_name"]
            product_price = upcDetailsAmazon["product_price"]
            product_description = upcDetailsAmazon["product_description"]
            product_category = 'Select'
            

            try:
                addFBListing = request.form["addFBListing"]
            except:
                addFBListing = 'off'


            try:
                imgpath = upcDetailsAmazon["product_image"]
            except:
                imgpath="Test1.png"
                
            link_img_link={}
            link_img_link['link'] = 'https://origamiitlab.com/wp-content/uploads/2018/12/bird.png'
            link_img_link['imglink'] = 'https://origamiitlab.com/wp-content/uploads/2018/12/bird.png'
                
            price1 = float(product_price.replace("$", ""))
        
            if disc=="" or disc=='0':
                discountedPrice=float(product_price.replace("$", ""))
            else:    
                disc1=float(disc)
                discP = price1 - ((price1*disc1)/100)
                discountedPrice = '%.2f' % discP

            product_price1 =  round(float(discountedPrice))  

            if(addFBListing=='on'):                              
                link_img_link = uploadToMP(product_name, product_price1, product_description, upc, "Miscellaneous", "New", imgpath)
                
                if int(product_price1)>int(InstaPrice):
                    writeInstaJson(upc, product_name, product_description, imgpath, product_price, disc, stock, employee, link_img_link['link'])

            itemCounter = update_details(upc, 
                                         product_name, 
                                         product_price, stock, disc, employee, link_img_link['link'], link_img_link['imglink'], product_description)
            
            count = itemCounter["count"]
            zpl = printlabel(upc, product_name, product_price, disc)

            add_to_square(product_name, upc, product_price + "00", employee, stock)

            
            try:
                printlabels = int(request.form["printlabels"])
            except:
                printlabels = 1
            
            imgname = open_acrobat_print(printlabels)
            
            
            
            # end time
            end = time.time()
            
            runtime = end - start
            print('runtime')
            print(runtime)
            categories = json.load(open(json_url))
            categoryFoundFlag = 0
            discountPercent = 0
            for name, discount in categories.items():
                if name in upcDetailsAmazon["product_category"]:  
                    categoryFoundFlag = 1
                    discountPercent = discount
                    
            default_details =   {
                                    "product_name":product_name,
                                    "product_price":product_price,
                                    "product_category": product_category,
                                }
            return render_template('amazon.html', 
                                   details=default_details, 
                                   duration=runtime, 
                                   counter=count, 
                                   zpl=zpl, 
                                   label=imgname, 
                                   walmart=0, 
                                   amazon=0, 
                                   categories=categories,
                                   categoryFoundFlag=categoryFoundFlag,
                                   discount = discountPercent)
        
        
        else:
            print('Report bad parameter')
    else: 
        categories = json.load(open(json_url))   
        categoryFoundFlag = 0
        discountPercent = 0
        
        default_details = {
                       "product_name":"Title",
                       "product_price":"$0",
                       "product_category": "Select"
                    }
        
        for name, discount in categories.items():
            if name in default_details["product_category"]:  
                categoryFoundFlag = 1
                discountPercent = discount
                
        
        return render_template('amazon.html', 
                               details=default_details,
                               duration=0,counter=0,
                               walmart=0,
                               amazon=0,
                               categories=categories,
                               categoryFoundFlag=categoryFoundFlag,
                               discount=discountPercent)

        
        
@app.route('/amazon_add_multiple', methods = ['GET', 'POST'])
def amazon_add_multiple():
    
    config = json.load(open(config_url))
    delay = int(config['Delay'])
    delayInMin = int(delay * 60)

    if request.method == "POST":

        if request.form["btn"] == 'Publish':

            description = request.form["Description"] 
            category = "Miscellaneous"
            condition = "New"         
            upc = datetime.datetime.now().strftime('%Y%m%d%H%M')
            SheetPath = request.form["SheetPath"]
            
            
            wb = load_workbook(SheetPath)
            sheet = wb.worksheets[0]

            row_count = sheet.max_row
            
            for i in range(2, row_count):
                
                product_name = sheet.cell(row = i, column = 2).value
                product_price = '$'+ str(sheet.cell(row = i, column = 1).value)
                amazon_link = sheet.cell(row = i, column = 3).value
                
                data = get_amazon_price_by_link(amazon_link)
        
                try:            
                    product_image_url = str(data['image'])        
                    urllib.request.urlretrieve(product_image_url, "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png")
                    product_image_name= 'Test1.png'
                except:
                    product_image_name= 'Test_default.png'

                
                # if data['price'] is not None:
                #     product_price = data['price']                    
                # elif data['deal'] is not None:
                #     product_price = data['deal']  
                # elif data['sale'] is not None:
                #     product_price = data['sale']                    
                # else:
                #     print('Not found in Amazon')
                #     product_price = 0

                # product_name = data['name']
                uploadToMP(product_name, product_price, description, upc, category, condition, product_image_name)
                time.sleep(delayInMin)     
            
            return render_template('addtomarketfromamazon.html', config=config)
 
    return render_template('addtomarketfromamazon.html', config=config)  


def writeInstaJson(upc, product_name, product_description, product_image, product_price, disc, stock, employee, link_to_mp_post):

    
    # python object to be appended
    new_data = {
        'upc': upc,
        'product_name': product_name,
        'product_description': product_description,
        'product_image': product_image,
        'product_price': product_price, 
        'disc': disc,
        'stock': stock, 
        'employee': employee,
        'link_to_mp_post': link_to_mp_post
        }

    with open(data_ig_url,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # check if UPC exist
        for upc_no in file_data["upc_details"]:
            if str(upc) == str(upc_no['upc']):
                return
            
        # Join new_data with file_data inside upc_details
        file_data["upc_details"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

    
    return

def writeAllDetailsInCSV(upc, product_name, product_description, product_image, product_price, disc, stock, employee):

    
    # python object to be appended
    new_data = {
        'upc': upc,
        'product_name': product_name,
        'product_description': product_description,
        'product_image': product_image,
        'product_price': product_price, 
        'disc': disc,
        'stock': stock, 
        'employee': employee
        }

    if os.path.isfile(data_date_url):
        # checks if file exists
        print ("File exists and is readable")
    else:
        print ("Either file is missing or is not readable, creating file...")
        with open(data_date_url, 'w') as db_file:
            db_file.write(json.dumps({"upc_details":[]}))


    with open(data_date_url,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # check if UPC exist
        for upc_no in file_data["upc_details"]:
            if upc == upc_no['upc']:
                return
            
        # Join new_data with file_data inside upc_details
        file_data["upc_details"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

    
    return

def delete_upc(upc):
    print("deleteing upc" + str(upc))
    data_array = json.load(open(data_url))
    df_data = pd.DataFrame(data_array['upc_details'])
    df_data.drop(df_data[df_data['upc'] == upc].index, inplace=True)
    data_dict = df_data.to_dict('records')
    # convert df to dict
    json_f = dict()
    json_f['upc_details'] = data_dict
    # df to json and save it to json file
    result = json.dumps(json_f, indent=4)
    jsonFile = open(data_url, "w")
    jsonFile.write(result)
    jsonFile.close()

def upload_products():

    config = json.load(open(config_url))
    data_array = json.load(open(data_url))
    delay = int(config['Delay'])
    delayInMin = int(delay * 60)
    InstaPrice = int(config['InstaPrice'])


    counter = 0

    for row in data_array['upc_details']:        

        upc = row['upc']
        product_name = row['product_name']
        product_description = row['product_description']
        product_image = row['product_image']
        product_price = row['product_price']
        disc = row['disc']
        stock = row['stock']
        employee = row['employee']

    
        try:                  
            urllib.request.urlretrieve(product_image, "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\Test1.png")   
            product_image_name= 'Test1.png'
        except:
            product_image = 'https://origamiitlab.com/wp-content/uploads/2018/12/bird.png'
            product_image_name= 'Test_default.png'
        

        try: 
            price1 = float(product_price.replace("$", ""))
        except:
            price1 = float(product_price)

        if disc=="" or disc=='0':
            discountedPrice=product_price
        else:    
            disc1=float(disc)
            discP = price1 - ((price1*disc1)/100)
            discountedPrice = '%.2f' % discP

        product_price1 =  round(float(discountedPrice)) 

        try:    
            print(product_name + " " + str(upc))    
            link_to_mp_post = uploadToMP(product_name, product_price1, product_description, upc, "Miscellaneous", "New", product_image_name)
            print('Posted to MP ' + link_to_mp_post['link'])
            if link_to_mp_post['link']=='':
                delete_upc(upc)


            if int(product_price1)>int(InstaPrice):
                writeInstaJson(upc, product_name, product_description, product_image, product_price, disc, stock, employee, link_to_mp_post)

            itemCounter = update_details(upc, product_name, product_price, stock, disc, employee, link_to_mp_post['link'], product_image, product_description)
            print('Posted to Catalog')

            count = itemCounter["count"]

            add_to_square(product_name, upc, str(product_price) + "00", employee, stock)
            print('Posted to Square')


        except Exception as e: 
            print(str(e))
            # os.system("taskkill /im chromedriver.exe /F")
            # os.system("taskkill /im chrome.exe /F")
            print('Failed UPC - ' + upc)


    return

def upload_products_to_ig():    
    
    data_array = json.load(open(data_ig_url))
    counter = 0

    for row in data_array['upc_details']:

        if counter==24:
            break

        upc = row['upc']
        product_name = row['product_name']
        product_description = row['product_description']
        product_image = row['product_image']
        product_price = row['product_price']
        disc = row['disc']
        stock = row['stock']
        employee = row['employee']
        link_to_mp_post = row['link_to_mp_post']


        try: 
            price1 = float(product_price.replace("$", ""))
        except:
            price1 = float(product_price)

        if disc=="" or disc=='0':
            discountedPrice=product_price
        else:    
            disc1=float(disc)
            discP = price1 - ((price1*disc1)/100)
            discountedPrice = '%.2f' % discP

        product_price1 =  round(float(discountedPrice)) 
        description = str(product_name) + """
        
        """ + str(link_to_mp_post) + """
        
        """ +'PRICE = $' + str(product_price1) 
        

        if(len(product_name)>109):
            description=product_name[0:2200]
        else:
            pass

        postInstagram(product_image, description)

        print('Posted to IG')

        counter = counter + 1

    return


@app.route('/', methods = ['GET', 'POST'])
def target():
    
    global upcDetails
    
    if request.method == "POST":
        link=request.form["TargetLink"]
        try:
            stock=request.form["Stock"]
        except:
            stock=0
        try:
            disc=request.form["Discount"]  
        except:
            disc=0
        

        if '' in request.form["printlabels"]:
            printlabels = 1
        else:
            printlabels = int(request.form["printlabels"])

             
        employee=request.form["VendorName"]   
        amazon_price =0 
        walmart_price = 0
        target_product_price=0
        
        

        
        if request.form["btn"] == 'Fetch Details':  
            # starting time
            start = time.time()
            
            
            upcDetailsTarget = get_price_name(link)
            
            lowest_price = 0
            upcDetails = upcDetailsTarget
            try:                
                target_product_price = upcDetailsTarget["product_price"]
                upc = upcDetailsTarget["upc"]
                lowest_price = float(target_product_price)
                upcDetails["lowest_price"] = lowest_price
            except:
                target_product_price = 0
                
            
            if 'Not Found' in upcDetails["product_name"]:
                print('Not found in Target')
                target_product_price="0"
                                

                
            end = time.time()
            
            runtime = end - start
            dur='%.2f' % runtime
            
                           
            for filename in os.listdir('static/'):
                if filename.startswith('label'):  # not to remove other images
                    imgname = filename
            
           
            categories = json.load(open(json_url))    
            categoryFoundFlag = 0
            discountPercent = 0
            for name, discount in categories.items():
                if name in upcDetails["product_category"]:  
                    categoryFoundFlag = 1   
                    discountPercent = discount
                       
            return render_template('target.html', 
                                   lowest_price = lowest_price,
                                   details=upcDetails, 
                                   duration=dur, 
                                   counter=0,  
                                   zpl="", 
                                   label=imgname, 
                                   target=target_product_price, 
                                   walmart=walmart_price, 
                                   amazon=amazon_price,
                                   categories=categories,
                                   categoryFoundFlag=categoryFoundFlag,
                                   discount = discountPercent)
            
        elif request.form["btn"] == 'Print Label':
            # starting time
            
            start = time.time()
            
            upc = upcDetails["upc"]
            product_name = upcDetails["product_name"]
            product_price = upcDetails["lowest_price"]
            product_description = upcDetails["product_description"]
            product_category = upcDetails["product_category"]
            product_image = upcDetails["product_image"]
            disc= request.form['Discount']


            writeAllDetailsInCSV(upc, product_name, product_description, product_image, product_price, disc, stock, employee)

            zpl = printlabel(upc, product_name, product_price, disc)

            
            try:
                printlabels = int(request.form["printlabels"])
            except:
                printlabels = 1
            
            imgname = open_acrobat_print(printlabels)
            
            
            
            # end time
            end = time.time()
            
            runtime = end - start
            print('runtime')
            print(runtime)
            categories = json.load(open(json_url))
            categoryFoundFlag = 0
            discountPercent = 0
            for name, discount in categories.items():
                if name in upcDetails["product_category"]:  
                    categoryFoundFlag = 1
                    discountPercent = discount
                    
            default_details =   {"upc":upc,
                                    "product_name":product_name,
                                    "product_price":product_price,
                                    "product_category": product_category,
                                }
            return render_template('target.html', 
                                   details=default_details, 
                                   duration=runtime, 
                                   counter=0000, 
                                   zpl=zpl, 
                                   label=imgname, 
                                   walmart=0, 
                                   amazon=0, 
                                   categories=categories,
                                   categoryFoundFlag=categoryFoundFlag,
                                   discount = discountPercent)
        
        elif request.form["btn"] == 'Upload Products':

            upload_products()

            categories = json.load(open(json_url))   
            categoryFoundFlag = 0
            discountPercent = 0
            
            default_details = {"upc":"",
                       "product_name":"Title",
                       "product_price":"$0",
                       "product_category": "Select"
                    }

            return render_template('target.html', 
                               details=default_details,
                               duration=0,counter=0,
                               walmart=0,
                               amazon=0,
                               categories=categories,
                               categoryFoundFlag=categoryFoundFlag,
                               discount=discountPercent)
    
        elif request.form["btn"] == 'Upload 25 to IG':

            upload_products_to_ig()

            categories = json.load(open(json_url))   
            categoryFoundFlag = 0
            discountPercent = 0
            
            default_details = {"upc":"",
                       "product_name":"Title",
                       "product_price":"$0",
                       "product_category": "Select"
                    }

            return render_template('target.html', 
                               details=default_details,
                               duration=0,counter=0,
                               walmart=0,
                               amazon=0,
                               categories=categories,
                               categoryFoundFlag=categoryFoundFlag,
                               discount=discountPercent)

        else:
            print('Report bad parameter')
    else: 
        categories = json.load(open(json_url))   
        categoryFoundFlag = 0
        discountPercent = 0
        
        default_details = {"upc":"",
                       "product_name":"Title",
                       "product_price":"$0",
                       "product_category": "Select"
                    }
        
        for name, discount in categories.items():
            if name in default_details["product_category"]:  
                categoryFoundFlag = 1
                discountPercent = discount
                
        
        return render_template('target.html', 
                               details=default_details,
                               duration=0,counter=0,
                               walmart=0,
                               amazon=0,
                               categories=categories,
                               categoryFoundFlag=categoryFoundFlag,
                               discount=discountPercent)

if __name__ == '__main__':
    app.run(debug=True)

    
