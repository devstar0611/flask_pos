'''
import labelary

test_label = "^XA^FX Top section with logo, name and address.^CF0,60^FO50,50^GB100,100,100^FS^FO75,75^FR^GB100,100,100^FS^FO93,93^GB40,40,40^FS^FO220,50^FDMESA LIQUIDATION.^FS^CF0,30^FO220,115^FD1250 W University Dr^FS^FO220,155^FDMesa, AZ 85201^FS^FO220,195^FDUnited States (USA)^FS^FO50,250^GB700,3,3^FS^FX Second section with recipient address and permit information.^CFA,30^FO50,300^FDPRODUCT NAME^FS^FO50,340^FDORIGINAL PRICE^FS^FO50,380^FDDISCOUNT^FS^FO50,420^FDOUR PRICE^FS^FO50,470^GB700,3,3^FS^FX Third section with barcode.^BY5,2,200^FO100,550^BC^FD12345678^FS^XZ"


png_labels = labelary.zpl2_to_png(test_label)

for i, label in enumerate(png_labels):
    with open('test_label{}.png'.format(i), 'wb') as fid:
        fid.write(label)

'''

import time
#from zebra import Zebra
import labelary
import os
import psutil

def open_acrobat_print(count):
    for i in range(int(count)):
        for filename in os.listdir('static/'):
            if filename.startswith('test_label'):  # not to remove other images
                imgname = filename
                break    
        
        os.startfile("static\\test_pdf_label.pdf", "print")
        time.sleep(1)

        for p in psutil.process_iter(): #Close Acrobat after printing the PDF
            if 'AcroRd' in str(p):
                p.kill()
            if 'Acrobat' in str(p):
                p.kill()
    
    return imgname
    

def printlabel(upc, product_name, product_price, disc):

    if(len(product_name)>109):
        product_name=product_name[0:109]
    else:
        pass

    print(product_name + str(product_price) + str(disc))
    '''    
    PN=bytes(product_name, encoding='utf-8')
    PP=bytes(product_price, encoding='utf-8')
    DISC=bytes(disc, encoding='utf-8')
    price1 = float(product_price.replace("$", ""))
    disc1=float(disc)
    discP = price1 - ((price1*disc1)/100)
    discountedPrice = '%.2f' % discP
    OP=bytes(discountedPrice, encoding='utf-8')
    UPC = bytes(upc, encoding='utf-8')
    '''

    a = "^XA ^FX Top section with logo, name and address. ^CF0,40 ^FO45,60^FDMESA LIQUIDATION^FS ^CF0,25 ^FO60,105^FD2665 E BROADWAY RD. B109^FS ^FO130,135^FDMesa, AZ 85204^FS ^FO20,190^GB360,3,3^FS  ^FX Second section with recipient address and permit information. ^CF0,25 ^FO20,210^FB350,5,6,L,0^FD"
    b = "^FS ^FO20,360^FDORIGINAL PRICE: "
    
    d = "^FS ^CF0,41 ^FO20,400^FDOUR PRICE: $"
    e = "^FS ^FO20,440^GB360,3,3^FS^FX Third section with bar code.^BY3,3,110 ^FO50,470,0^BC,80,N,N,N,A^FD"
    f = "^FS ^XZ"
    
    try:
        price1 = float(product_price.replace("$", ""))
    except:
        price1=float(product_price)
    
    if disc=="" or disc=='0':
        discountedPrice=product_price
        raw_data = a + product_name + d + str(discountedPrice) + e + upc + f
    else:    
        disc1=float(disc)
        discP = price1 - ((price1*disc1)/100)
        discountedPrice = '%.2f' % discP
    
        raw_data = a + product_name + b + str(product_price) + d + discountedPrice + e + upc + f
    #braw=bytes(raw_data, encoding='utf-8')
    #z = Zebra("ZDesigner LP 2844")
    #z.setup()
    #z.output(raw_data)
    for filename in os.listdir('static/'):
                if filename.startswith('test_label'):  # not to remove other images
                    os.remove('static/' + filename)
                    break
                    
    png_labels = labelary.zpl2_convert(raw_data.encode('utf-8'), output_type='png', resolution=8, width=2, height=3, index=None)
    pdf_labels = labelary.zpl2_convert(raw_data.encode('utf-8'), output_type='pdf', resolution=8, width=2, height=3, index=None)

    for i, label in enumerate(png_labels):
        with open('static/test_label' + str(time.time()) + '.png', 'wb') as fid:
            fid.write(label)
            
    for i, label in enumerate(pdf_labels):
        with open('static/test_pdf_label.pdf', 'wb') as fid:
            fid.write(label)
            
    return(raw_data)
'''
    a = b"^XA  ^FX Top section with logo, name and address. ^CF0,40 ^FO45,60^FDMESA LIQUIDATION^FS ^CF0,25 ^FO60,105^FD2665 E BROADWAY RD. B109^FS ^FO130,135^FDMesa, AZ 85204^FS ^FO20,190^GB360,3,3^FS  ^FX Second section with recipient address and permit information. ^CFA,20 ^FO20,210^FB350,3,6,L,0^FDPRODUCT NAME: "
    b = b"^FS  ^FO20,300^FDORIGINAL PRICE: "
    c = b"^FS ^FO20,330^FDDISCOUNT: "
    d = b"^FS ^CF0,35 ^FO20,370^FDOUR PRICE: "
    e = b"^FS ^FO20,410^GB700,3,3^FS  ^FX Third section with bar code. ^BY3,3,160 ^FO50,450,0^BC,100,N,N,N,A^FD"
    f = b"^FS ^XZ"
    #^XA  ^FX Top section with logo, name and address. ^CF0,40 ^FO45,60^FDMESA LIQUIDATION^FS ^CF0,25 ^FO60,105^FD2665 E BROADWAY RD. B109^FS ^FO130,135^FDMesa, AZ 85204^FS ^FO20,190^GB360,3,3^FS  ^FX Second section with recipient address and permit information. ^CFA,20 ^FO20,210^FB350,3,6,L,0^FDPRODUCT NAME: Barbie Care Clinic Playset^FS  ^FO20,300^FDORIGINAL PRICE: $49.99^FS ^FO20,330^FDDISCOUNT: 10%^FS ^CF0,35 ^FO20,370^FDOUR PRICE: $44.99^FS ^FO20,410^GB700,3,3^FS  ^FX Third section with bar code. ^BY3,3,160 ^FO50,450,0^BC,100,N,N,N,A^FD887961628739^FS ^XZ
    #raw_data = b"^XA^FX Top section with logo, name and address.^CF0,60^FO50,50^GB100,100,100^FS^FO75,75^FR^GB100,100,100^FS^FO93,93^GB40,40,40^FS^FO220,50^FDMESA LIQUIDATION.^FS^CF0,30^FO220,115^FD1250 W University Dr^FS^FO220,155^FDMesa, AZ 85201^FS^FO220,195^FDUnited States (USA)^FS^FO50,250^GB700,3,3^FS^FX Second section with recipient address and permit information.^CFA,30^FO50,300^FDPRODUCT NAME: ^FS^FO50,340^FDORIGINAL PRICE: ^FS^FO50,380^FDDISCOUNT: ^FS^FO50,420^FDOUR PRICE: ^FS^FO50,470^GB700,3,3^FS^FX Third section with barcode.^BY5,2,200^FO100,550^BC^FD12345678^FS^XZ"
    raw_data = a + PN + b + PP + c + DISC + d + OP + e + UPC + f
    
    #z = zebra("ZDesigner LP 2844")
    #z.output(raw_data)
    
    for i, label in enumerate(png_labels):
        with open('static/test_label{}.png'.format(i), 'wb') as fid:
            fid.write(label)

    mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)         
    host = "127.0.0.1" 
    port = 9100   
    try:           
        mysocket.connect((host, port)) #connecting to host
        mysocket.send(raw_data)#using bytes
        mysocket.close () #closing connection
    except:
        print("Error with the connection")
        
'''


