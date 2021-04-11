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
from selenium.webdriver.chrome.options import Options
from playsound import playsound
#from pyvirtualdisplay import Display


class bot():
    def __init__(self, items = [], site = "newegg"):
        
        #if site == "Amazon" or site == "amazon":
        #    continue
        if site == "newegg":
            self.siteParams = {'url':'http://www.newegg.com/global/il-en/','search': '//input[@title="Search Site"]','https':"https://www.newegg.com/global/il-en/",'nextPage':'//button[@title="Next" and 1]',
            "items":'//div[@class="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell"]/div','onlyGPU':'//a[@title="Desktop Graphics Cards"]','name':'.//a[@title="View Details"]',
            'price':'.//li[@class="price-current "]/strong','isGood':['item-msg',"price-save-label"],'stock':'.//p[@class="item-promo"]',"searchURL":"https://www.newegg.com/global/il-en/p/pl?d=","extraParams":"",
            "filters":'//div[@class="left-nav"]/dl','filter type':'.//dt','departments':'.//dd/*/a','filter target type':"Department"}
        else:
            self.siteParams = {'url':'http://www.newegg.com/global/il-en/','search': '//input[@title="Search Site"]','https':"https://www.newegg.com/global/il-en/",'nextPage':'//button[@title="Next" and 1]',
            "items":'//div[@class="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell"]/div','onlyGPU':'//a[@title="Desktop Graphics Cards"]','name':'.//a[@title="View Details"]',
            'price':'.//li[@class="price-current "]/strong','isGood':['item-msg',"price-save-label"],'stock':'.//p[@class="item-promo"]',"searchURL":"https://www.newegg.com/global/il-en/p/pl?d=","extraParams":"",
            "filters":'//div[@class="left-nav"]/dl','filter type':'.//dt','departments':'.//dd/*/a','filter target type':"Department"}
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--silent")
        
        self.items = items
        self.network_url = self.siteParams['https']
        # url of LinkedIn sales
        self.url =  self.siteParams['url']
        # The 3 web browsers for the bot
        self.driver = webdriver.Chrome('chromedriver.exe',options=chrome_options)
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


    
    def searchItems(self,items=[]):
        self.data = {"Name":[],"Link":[],"Stock":[],"Is good":[],"Price":[]}
        #make sure we have one of each item
        items.extend(self.items)
        temp = set(items)
        items = list(temp)
        xPath = self.siteParams["search"]
        for i in range(len(items)):
            if type(items[i]) == str:
                items[i] = tuple(items[i],"")
            elif len(items[i]) != 2:
                items[i] = tuple(items[i][0],"")
        
        for item in items:
            #search
            self.driver.execute_script("window.scrollTo(0, 0);")
            search = self.siteParams["searchURL"]+item[0].replace(' ','+')
            self.driver.get(search)
            #fillter to department
            newURL = self.getDepartment(item[1])
            if newURL != "":
                self.driver.get(newURL)
            
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
                     print("error")
                
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


    def getDepartment(self,item):
        
        department = None
        if len(item)==0:
            return ""
        try:
            # get the list of all filters
            filterList = WebDriverWait(self.driver, 50).until(EC.presence_of_all_elements_located((By.XPATH, self.siteParams["filters"])))
        except:
            filterList = []
            return ""
        for filterType in filterList:
            if self.siteParams["filter target type"] == filterType.find_element_by_xpath(self.siteParams["filter type"]).text:
                department = filterType
        if department != None:
            try:
                # get the list of departments
                departments = department.find_elements_by_xpath(self.siteParams["departments"])
            except:
                departments = []
            for dep in departments:
                if dep.get_attribute("title") == item:
                    return dep.get_attribute("href")
        return ""
            
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

    def getFound(self):
        found = {"Name":[],"Link":[],"Stock":[],"Is good":[],"Price":[]}
        for i in range(len(self.data["Name"])):
            if self.data["Is good"][i] == "Looking to buy" and self.data["Stock"][i] == "------IN STOCK------":
                found["Stock"].append(self.data["Stock"][i])
                found["Is good"].append(self.data["Is good"][i])
                found["Price"].append(self.data["Price"][i])
                found["Name"].append(self.data["Name"][i])
                found["Link"].append(self.data["Link"][i])
        return found


    def kill(self):
        self.driver.close()

                




gpuStock = bot(items=[("rtx 3060 ti","Video Cards & Video Devices"),("rtx 3070","Video Cards & Video Devices")],site = "newegg")
#gpuStock = bot(items=[("intel i7 10700k","CPUs / Processors")],site = "newegg")

n = 0
while True:
    n+=1
    gpuStock.searchItems()
    found = gpuStock.getFound()
    #found stock
    if len(found["Name"])>0:
        found = pd.DataFrame(data=found)
        playsound("data/found.mp3")
        print(found)
    print("looked",n,"times")
gpuStock.kill()
#display.stop()
print("done")
