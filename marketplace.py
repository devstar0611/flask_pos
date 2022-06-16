from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.webdriver.common.action_chains import ActionChains

import time
import pyautogui
from time import sleep
import pyperclip
import os


profilePath= "C:\\Users\\justs\\AppData\\Local\\Google\\Chrome\\User Data"

options = Options()
# options.add_argument('--headless')
#options.add_argument('--no-sandbox')
options.add_argument("--disable-notifications")
options.add_argument('--start-maximized')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--ignore-certificate-errors")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("user-data-dir="+ profilePath)



def uploadToMP(title, price, description, sku, category, condition, imagename):

   
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    try:
        driver.switch_to_window(driver.window_handles[0])



        driver.get("https://www.facebook.com/marketplace/create/item")


        driver.execute_script("document.body.style.zoom='100%'")
        
        myTitle = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//label[@aria-label='Title']//input")))
        myPrice = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//label[@aria-label='Price']//input")))
        mySKU = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//label[@aria-label='SKU']//input")))
        myCategoryDD = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Category']")))
        myConditionDD = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//label[@aria-label='Condition']")))
        myAddPhotos = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//span[text()='Add Photos']")))
        myDescription = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//textarea")))   


        # create action chain object
        action = ActionChains(driver)  
        # # perform the operation
        action.move_to_element(myTitle).click().perform()
        pre_Title = "MESA LIQUIDATION - Target Overstock - "
        title = pre_Title + title
        myTitle.send_keys(title[0:99])



        action.move_to_element(myPrice).click().perform()
        myPrice.send_keys(price)
        action.send_keys(Keys.TAB).perform()




        action_category = ActionChains(driver) 
        #click on category dropdown
        action_category.move_to_element(myDescription).click().perform() 
        time.sleep(1)
        myCategoryDD.send_keys("Miscellaneous")
        time.sleep(1)
        myCategoryTools = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[starts-with(text(), 'Miscellaneous')]")))
        driver.execute_script("arguments[0].click();", myCategoryTools)
        action_category.send_keys(Keys.TAB).perform()




        # #click on condition dropdown
        action_condition = ActionChains(driver) 
        action_condition.move_to_element(myDescription).perform()
        driver.execute_script("arguments[0].click();", myConditionDD)
        time.sleep(2)
        myCondition = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@role='menu']//span[text()='New']")))
        driver.execute_script("arguments[0].click();", myCondition)
        action_condition.send_keys(Keys.TAB).perform()


        
        action_description = ActionChains(driver)  
        action_description.move_to_element(myDescription).click().perform() 
        time.sleep(1)
        pre_description = """
        We are called: MESA LIQUIDATION
        Address: 2665 E Broadway Road. B109, Mesa, AZ 85204
        Google Maps: https://tinyurl.com/3dm7vwsy

        Business Hours: Monday to Friday - 10 AM to 8PM,
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

        Horario comercial: de lunes a viernes de 10 a. M. A 8 p. M.,
        Sábado - 10 a. M. A 6 p. M.
        Domingo - CERRADO.
        PH: (480) 306-8725

        Somos una instalación de exceso de existencias objetivo, que transporta productos para bebés, ropa, zapatos, cosméticos, mercancía general, carteras, mochilas y mucho más. Tenemos un 40 a 90% de descuento en la mayoría de los casos con respecto al MSRP.

        Por favor hazme saber si tienes preguntas.


        """
        description = pre_description + description
        pyperclip.copy(description)
        myDescription.send_keys(Keys.CONTROL + "v")
        action_sku = ActionChains(driver)  
        action_sku.move_to_element(mySKU).click().perform()
        mySKU.send_keys(sku)

        
        #click on Photo     
        # action_photo.move_to_element(myAddPhotos).click().perform()
        myAddPhotos.click()
        imagepath = "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\" + imagename
        print(imagepath)
        time.sleep(2)
        pyautogui.write(imagepath) 
        pyautogui.press('enter')
        time.sleep(3)
        # imagepath = "C:\\Users\\justs\\OneDrive\\Pictures\\ProductImages\\" + imagename
        # driver.FindElement(By.XPath("//input[@type='file'][1]")).SendKeys(imagepath)
        
        # action_Nextbt = ActionChains(driver)  
        myNextBtn = WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Next']")))
        # action_Nextbt.move_to_element(myNextBtn).perform()
        # myNextBtn.click()
        driver.execute_script("arguments[0].click();", myNextBtn)
        time.sleep(4)
        
        #check url
        if('step=delivery' in driver.current_url):
            #action.move_to_element(myNextBtn).perform()
            myNextBtn1 = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Next']")))
            # myNextBtn1.click()
            driver.execute_script("arguments[0].click();", myNextBtn1)
            time.sleep(5)


        #check url
        # if('step=audience' in driver.current_url):
        myPublishBtn = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Publish']")))
        # myPublishBtn.click()
        driver.execute_script("arguments[0].click();", myPublishBtn)
        print('Publish')
        time.sleep(5)
            
        #Get listing URL
        # if('selling' in driver.current_url):

        
        # click on hide if exists
        try:
            myHideLink = WebDriverWait(driver, 40).until(EC.presence_of_element_located(
                (By.XPATH, "//span[text()='Needs attention']/parent::span/parent::h2/parent::div/parent::div//div[2]//span[text()='Hide']"))) 
            driver.execute_script("arguments[0].click();", myHideLink)
        except:
            print('Not found More')


        myMoreButton = WebDriverWait(driver, 40).until(EC.presence_of_element_located(
            (By.XPATH, "//div[@aria-label='More'][1]")))
        driver.execute_script("arguments[0].click();", myMoreButton)
        
        #Get URL
        myListingMenuItem = WebDriverWait(driver, 40).until(EC.presence_of_element_located(
            (By.XPATH, "//a[@role='menuitem'][1]")))
        link = myListingMenuItem.get_attribute("href")
        print(link)

        # Get Img link
        myImgUrl = WebDriverWait(driver, 40).until(EC.presence_of_element_located(
            (By.XPATH, "//div/img[@referrerpolicy='origin-when-cross-origin']")))
        imglink = myImgUrl.get_attribute("src")
        print(imglink)
        
        
        driver.close()
        driver.quit()

        return {
        "link":link,
        "imglink":imglink
            }

    except Exception as e:
        print(str(e))
        driver.close()
        driver.quit()

    return {
    "link":'',
    "imglink":''
        }
    
    




def publish(title, price, description, sku, category, condition, CoverImagePath, ImageCount):

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.switch_to_window(driver.window_handles[0])
    driver.get("https://www.facebook.com/marketplace/create/item")
    driver.execute_script("document.body.style.zoom='100%'")
    
    myTitle = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//label[@aria-label='Title']//input")))
    myPrice = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//label[@aria-label='Price']//input")))
    mySKU = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//label[@aria-label='SKU']//input")))
    myCategoryDD = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Category']")))
    myConditionDD = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//label[@aria-label='Condition']")))
    myAddPhotos = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//span[text()='Add Photos']")))
    myDescription = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//textarea")))   


    # create action chain object
    action = ActionChains(driver)  
    action.move_to_element(myTitle).click().perform()
    myTitle.send_keys(title[0:99])


    action.move_to_element(myPrice).click().perform()
    myPrice.send_keys(price)
    action.send_keys(Keys.TAB).perform()




    action_category = ActionChains(driver) 
    #click on category dropdown
    action_category.move_to_element(myDescription).click().perform() 
    time.sleep(1)
    myCategoryDD.send_keys("Miscellaneous")
    time.sleep(1)
    myCategoryTools = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[starts-with(text(), 'Miscellaneous')]")))
    driver.execute_script("arguments[0].click();", myCategoryTools)
    action_category.send_keys(Keys.TAB).perform()




    # #click on condition dropdown
    action_condition = ActionChains(driver) 
    action_condition.move_to_element(myDescription).perform()
    driver.execute_script("arguments[0].click();", myConditionDD)
    time.sleep(2)
    myCondition = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@role='menu']//span[text()='New']")))
    driver.execute_script("arguments[0].click();", myCondition)
    action_condition.send_keys(Keys.TAB).perform()


    
    action_description = ActionChains(driver)  
    action_description.move_to_element(myDescription).click().perform() 
    time.sleep(1)    
    pyperclip.copy(description)
    myDescription.send_keys(Keys.CONTROL + "v")



    action_sku = ActionChains(driver)  
    action_sku.move_to_element(mySKU).click().perform()
    mySKU.send_keys(sku)

    
    #click on Photo 
    imagepath = " "
    for count in range(0, int(ImageCount)):
        imagepath =  imagepath + '"' + CoverImagePath + '\\' + os.listdir(CoverImagePath)[count]  + '"'
    

    myAddPhotos.click()
    time.sleep(1)
    pyautogui.write(imagepath) 
    pyautogui.press('enter')
    time.sleep(3)
    imagepath = " "
    
    # action_Nextbt = ActionChains(driver)  
    myNextBtn = WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Next']")))
    # action_Nextbt.move_to_element(myNextBtn).perform()
    # myNextBtn.click()
    driver.execute_script("arguments[0].click();", myNextBtn)
    time.sleep(4)
    
    #check url
    if('step=delivery' in driver.current_url):
        #action.move_to_element(myNextBtn).perform()
        myNextBtn1 = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Next']")))
        # myNextBtn1.click()
        driver.execute_script("arguments[0].click();", myNextBtn1)
        time.sleep(5)


    #check url
    # if('step=audience' in driver.current_url):
    myPublishBtn = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Publish']")))
    # myPublishBtn.click()
    driver.execute_script("arguments[0].click();", myPublishBtn)
    print('Publish')
    time.sleep(5)
        

    driver.close()
    driver.quit()

    for count in range(0, int(ImageCount)):
        try:
            os.remove(CoverImagePath + '\\' + os.listdir(CoverImagePath)[count])
        except:
            pass
    
