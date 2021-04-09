#import pyodbc
import string
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pyautogui as pag
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains as A
import pandas as pd
from time import sleep
class bot():
    def __init__(self, items = [], site = "newegg"):
        
        #if site == "Amazon" or site == "amazon":
        #    continue
        if site == "newegg":
            self.siteParams = {'url':'http://www.newegg.com/global/il-en/','search': '//input[@title="Search Site"]','https':"https://www.newegg.com/global/il-en/",'nextPage':'//button[@title="Next" and 1]',
            "items":'//div[@class="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell"]/div','onlyGPU':'//a[@title="Desktop Graphics Cards"]','name':'.//a[@title="View Details"]',
            'price':'.//li[@class="price-current "]/strong','isGood':['item-msg',"price-save-label"],'stock':'.//p[@class="item-promo"]'}
        else:
            self.siteParams = {'url':'http://www.newegg.com/global/il-en/','search': '//input[@title="Search Site"]','https':"https://www.newegg.com/global/il-en/",'nextPage':'//button[@title="Next" and 1]',
            "items":'//div[@class="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell"]/div','onlyGPU':'//a[@title="Desktop Graphics Cards"]','name':'.//a[@title="View Details"]',
            'price':'.//li[@class="price-current "]/strong','isGood':['.//p[@class="item-msg"]','.//li[@class="price-save "]/span[@class="price-save-label"]'],'stock':'.//p[@class="item-promo"]'}
        
        
        self.items = items
        self.network_url = self.siteParams['https']
        # url of LinkedIn sales
        self.url =  self.siteParams['url']
        # The 3 web browsers for the bot
        self.driver = webdriver.Chrome('chromedriver.exe')
        self.driver.get(self.url)
        self.searchItems(self.items)
    
    #get html element with xpath
    def getElem(self,xpathLoc,browser=None):
            
            if browser==None:
                browser = self.driver
            try:

                # Will wait 10 seconds for the element to be present
                elem = WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.XPATH, xpathLoc))
                )
            except:
                #print("error")
                #print("location: " + xpathLoc + " does not exist!")
                return None
                #self.driver.quit()
            return elem


    
    def searchItems(self,items,onlyGPU=True):
        self.data = {"Name":[],"Link":[],"Stock":[],"Is good":[],"Price":[]}
        
        xPath = self.siteParams["search"]
        
        for item in items:
            #search
            self.driver.execute_script("window.scrollTo(0, 0);") 
            searchBar = self.getElem(xPath)
            searchBar.clear()
            searchBar.send_keys(item + Keys.ENTER)

            #fillter to only gpu
            self.getElem(self.siteParams["onlyGPU"]).click()
            
            #go to next page
            url = ""
            while url != self.driver.current_url:
                nextP = self.getElem(self.siteParams["nextPage"])
                url = self.driver.current_url
                # Scroll down to load all of the people
                y = 0
                while True:
                    # Scroll down to bottom
                    self.driver.execute_script("window.scrollTo(0, "+str(y)+");") 
                    sleep(0.005)
                    if y >= self.driver.execute_script("return document.body.scrollHeight;"):
                        break
                    y = y+100
                
                try:
                    # get the list of items
                    itemList = WebDriverWait(self.driver, 50).until(
                        EC.presence_of_all_elements_located((By.XPATH, self.siteParams["items"]))
                    )
                except:
                    #print("error")
                
                #converts all the findings into a dictionary
                self.makePretty(itemList)
                if nextP:
                    try:
                        nextP.click()
                    except:
                        break
        self.df = pd.DataFrame(data=self.data)
        self.df.to_csv('stock report.csv', index=False)
        return self.df



            
    def makePretty(self,items):

        for item in items:
            name = item.find_element_by_xpath(self.siteParams["name"])
            
            link = name.get_attribute("href")
            name = name.text
            price = item.find_element_by_xpath(self.siteParams["price"]).text
            good = False
            prob = ""
            try:
                for params in self.siteParams["isGood"]:
                    prob = params
                    if len(item.find_elements_by_class_name(params)) > 0:
                        good = True
            except:
                good = False
                print(prob)
            stock = False
            try:
                if item.find_element_by_xpath(self.siteParams["stock"]) == []:
                    stock = True
            except:
                stock = True
            self.data["Name"].append(name)
            self.data["Link"].append(link)
            if stock:
                stock = "------IN STOCK------"
            else:
                stock = "OUT OF STOCK"
            if good:
                good = "Looking to buy"
            else:
                good = "Not looking to buy"
            self.data["Stock"].append(stock)
            self.data["Is good"].append(good)
            self.data["Price"].append(price)
        return self.data
    def kill(self):
        self.driver.close()

                




gpuStock = bot(items=["rtx 3060 ti","rtx 3070"],site = "newegg")
gpuStock.kill()
print("done")
    

    