import json
# from instabot import Bot

# bot = Bot()

# bot.login(username = "******",
#           password = "ppppppp")


# bot.upload_photo("Test1.png",
#                  caption ="""
#                  MESA LIQUIDATION - Target Overstock - Kemon Zero Gravity Folding Lounge Outdoor Patio Adjustable Re		
# We are called: MESA LIQUIDATION		
# Address: 2665 E Broadway Road. B109, Mesa, AZ 85204		
# Google Maps: https://tinyurl.com/3dm7vwsy		
		
# Business Hours: Monday to Friday - 10 AM to 7PM,		
# Saturday - 10 AM to 6PM.		
# Sunday - CLOSED.		
# PH: (480) 306-8725		
# We are a target overstock facility, carrying Baby products, Clothing, Shoes, Cosmetics, General merchandise, Purses, Bag Packs and much more. We are 40 to 90% off in most cases from Target MSRP.		
		
# Please let us know if you have any questions.		
# ---------------------------------		
# Gracias por tu mensaje.		
# Nos llamamos: MESA LIQUIDACIÓN y sí es una ubicación física.		
		
# Ubicado en add: 2665 E Broadway Road. B109, Mesa, AZ 85204		
# Google Maps: https://tinyurl.com/3dm7vwsy		
		
# Horario comercial: de lunes a viernes de 10 a. M. A 7 p. M.,		
# Sábado - 10 a. M. A 6 p. M.		
# Domingo - CERRADO.		
# PH: (480) 306-8725		
		
# Somos una instalación de exceso de existencias objetivo, que transporta productos para bebés, ropa, zapatos, cosméticos, mercancía general, carteras, mochilas y mucho más. Tenemos un 40 a 90% de descuento en la mayoría de los casos con respecto al MSRP.		
		
# Por favor hazme saber si tienes preguntas.		
# """)


import requests
from yaml import tokens

# Every two months get new access tokens
# https://graph.facebook.com/v12.0/oauth/access_token?
# grant_type=fb_exchange_token&
# client_id=263357142480378&
# client_secret=be40a678886e36ec6c61d2630985affb&
# fb_exchange_token=EAADvhZAztNfoBALHC6rmYpuzrFSzEZAlSZBZCASREXH6klbGxolakQYhKAZBVZAcDl61Xcn7oZBlZCbnqZAhCZAFBYCTt0bd8k5U4mqaZB9VC42zGzzFvMbjoiD64cZCHjBdMKHyp0T6NwyYZBvVJ0OgKKnUvkel2sWql6rnMtvFUZBnzYV3JBb80PXsHZBAQIhwiDfascQQj9pe37vPQXJHB3hjOP9mPBZBKZB1A7UR7fZBnPQGfodpmGObXuVTcW3miXMnSVGpkZD

access_token = 'EAADvhZAztNfoBAI8YkM0jPB8bM7JoTRxfSeyZCGMknZAMtQ8A5z9dGZCVgLGjNnn3Etdi1gbY7TIoZChqoCe0dVSPsWnFF4BS63lQeSlRskNBhsZAxl94wg85R3mtEr5K5KeWX7fV3FUdr4FA2iZCuWevy6ZB9s8jsosowZB20ggjFt1r0iX3cpTmsZBQZAUtS4jlkZD'

def postInstagram(image_url, product_title):
    

    caption = product_title + """

        MESA LIQUIDATION - Target Overstock - Kemon Zero Gravity Folding Lounge Outdoor Patio Adjustable Re		
        We are called: MESA LIQUIDATION		
        Address: 2665 E Broadway Road. B109, Mesa, AZ 85204		
        Google Maps: https://tinyurl.com/3dm7vwsy		
                
        Business Hours: Monday to Friday - 10 AM to 7PM,		
        Saturday - 10 AM to 6PM.		
        Sunday - CLOSED.		
        PH: (480) 306-8725		
        We are a target overstock facility, carrying Baby products, Clothing, Shoes, Cosmetics, General merchandise, Purses, Bag Packs and much more. We are 40 to 90% off in most cases from Target MSRP.		
                
        Please let us know if you have any questions.		
        ---------------------------------		
        Gracias por tu mensaje.		
        Nos llamamos: MESA LIQUIDACIÓN y sí es una ubicación física.		
                
        Ubicado en add: 2665 E Broadway Road. B109, Mesa, AZ 85204		
        Google Maps: https://tinyurl.com/3dm7vwsy		
                
        Horario comercial: de lunes a viernes de 10 a. M. A 7 p. M.,		
        Sábado - 10 a. M. A 6 p. M.		
        Domingo - CERRADO.		
        PH: (480) 306-8725		
                
        Somos una instalación de exceso de existencias objetivo, que transporta productos para bebés, ropa, zapatos, cosméticos, mercancía general, carteras, mochilas y mucho más. Tenemos un 40 a 90% de descuento en la mayoría de los casos con respecto al MSRP.		
                
        Por favor hazme saber si tienes preguntas.		
    """


    post_url = "https://graph.facebook.com/17841447065898202/media"

    payload = {
        'image_url' : image_url,
        'caption': caption,
        'access_token': access_token
    }

    r= requests.post(post_url, data=payload)
    # print(r.text)

    result = json.loads(r.text)
    if 'id' in result:
        creation_id = result['id']
        
        second_url = "https://graph.facebook.com/17841447065898202/media_publish"
        second_payload = {
            'creation_id':creation_id,
            'access_token': access_token
        }

        r= requests.post(second_url, data=second_payload)
        print(r.text)
    else:
        print('Error')

    
    return




