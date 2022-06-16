import pygsheets
import pandas as pd

from printzpls import printlabel

from datetime import datetime


#authorization
gc = pygsheets.authorize(service_file='client_secret.json')




def update_details(upc, title, price, stock, disc, employee):
    
    zplgen = printlabel(upc, title, price, disc)
                
     # Create empty dataframe
    df = pd.DataFrame()

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open('Target')


    #select the first sheet 
    wks = sh.sheet1
    
    
    j=0
    for row in wks:
        j=j+1

    j=j+1
    i=str(j)
    
    c1 = wks.cell('A' + i)
    c1.value= upc
    
    c2 = wks.cell('B' + i)
    c2.value= title
    
    c3 = wks.cell('C' + i)
    c3.value= price
    
    c4 = wks.cell('D' + i)
    if stock=="":
        c4.value= 1
    else:
        c4.value= stock
    
    c5 = wks.cell('E' + i)
    c5.value= disc
    
    
    c6 = wks.cell('F' + i)   
    if disc=="":
        c6.value= 0
    else:
        price1 = float(price.replace("$", ""))
        disc1=float(disc)
        discP = price1 - ((price1*disc1)/100)
        
        c6.value= '%.2f' % discP

    
    c7 = wks.cell('G' + i)
    c7.value= str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
    
    c8 = wks.cell('H' + i)
    c8.value= employee
    
    return {"count":i,
            "zpl":zplgen
            }


def get_price_title_from_upc(scannedupc):
    sh = gc.open('Target')
    wks = sh.sheet1
    i=0
    for row in wks:
        i=i+1
        if scannedupc in wks[i][0]:
            title = wks[i][1]
            price = wks[i][2]
            stock = wks[i][3]
            mkt = wks[i][4]
            #print(price)
            #print(price)
            #print(title)
            return{
                "upc":scannedupc,
                "product_name":title,
                "product_name":price
            } 
      
    return(0)

