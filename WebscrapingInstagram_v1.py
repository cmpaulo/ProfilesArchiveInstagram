#!/usr/bin/env python3
# coding: utf-8

# # Web Scraping Instagram with Selenium

from unicodedata import name
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time

class BotInstagram():


    def __init__(self):
        
        option = webdriver.ChromeOptions()
        # option.add_argument('headless')
        self.driver = webdriver.Chrome('/home/claudio/Downloads/Chrome/chromedriver',options=option)
    

    def address(self, link):
        
        self.driver.get(link)
    

    def login_ig(self, user = '', passd = ''):
        
        self.username = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
        self.password = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

        #enter username and password
        # perfilarquivologia 
        self.username.clear()
        self.username.send_keys(user)
        self.password.clear()
        self.password.send_keys(passd)

        button = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        not_now = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Agora não")]'))).click()
        not_now2 = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Agora não")]'))).click()
    

    def search_words(self, keywords):

        #target the search input field
        self.searchbox = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Pesquisar']")))
        self.searchbox.clear()

        #search for the any
        self.searchbox.send_keys(keywords)
        time.sleep(2)
        divs = self.driver.find_elements(By.CLASS_NAME, 'fuqBx')

        return divs
        

    def get_status_and_follow_profiles(self, urls, follow = True):

        self.address(urls)
        time.sleep(3)
       
        try:
            posting = self.driver.find_element(By.XPATH,'/html/body/div[1]/section/main/div/header/section/ul/li[1]/div/span').text

        except:
            posting = "0" 
            print("Public - Not found")

        try:
            followers = self.driver.find_element(By.XPATH,'/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/div/span').text

        except:
            followers = "0"
            print("Followers - Not found")

        if follow:
            try:
                followbutton = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button')))
                if followbutton.text == "Seguir" or followbutton.text == "Follow":
                    followbutton.click()
                    print(' ### ### Following up new profile. !!!')
                else:
                    pass
            except:
                pass

        return posting,followers


    def quit(self):

        self.driver.quit()



bot = BotInstagram()

bot.address('http://www.instagram.com')

with open('login_out.txt') as userfile:
    line = userfile.readline() 
    usuario, senha = line.strip().split(' ')

bot.login_ig(user = usuario, passd = senha)


# open keywords keywords.txt files and save list lista.txt. 
find_profiles = []

with open('lista.txt','w') as filew,  open('keywords.txt','r') as words:

    search_word = words.readlines()

    for iw in search_word:

        divs = bot.search_words(f'{iw.split()[0].strip()}')
    
        for div in divs:

            print(f"_{iw.split()[0]}_")
            elements = div.find_elements(By.TAG_NAME, 'a')

            
            for element in elements:

                link = element.get_attribute("href")
                
                if link not in find_profiles:
                    
                    if "tags" not in link:
                        find_profiles.append(link)
                        
                        filew.write(link)
                        filew.write('\n')
                    else: 
                        continue
                else: 
                    continue

words.close()

filew.close()

# filter data from lista.txt
import pandas as pd
from datetime import date


data = pd.read_csv('lista.txt',names=['urls_pf'])

ndata = data.drop_duplicates(keep='last').sort_values('urls_pf')


outdata = pd.DataFrame(columns=['NumeroSeguidores','NumeroPostagens','@Perfil','url'])

# open each profile and scrap followers and number of publications.
def string_ptbr_tonumber(number_string):
    
    if type(number_string) == float:
        
        valor = int(number_string)

    else:

        if "," in number_string:
            valor = number_string.replace(",",".").replace('mil','')
            valor = int(float(valor)*1000)
            
        elif "." in number_string:
            valor = number_string.replace(".","")
            valor = int(float(valor))
            
        elif "mil" in number_string:
            valor = number_string.replace('mil','')
            valor = int(float(valor)*1000)
            
        else:
            valor = int(number_string)


    return valor


for iw in ndata.values:
    iw=iw[0]

    notag = iw.strip().split('/')

    if len(notag) < 6:
        post,follow = bot.get_status_and_follow_profiles(iw.strip(), follow=True)
    
        profileig = iw.strip().split('/')[-2]

        urllink = iw.strip()
        
        nflw = string_ptbr_tonumber(follow)
        npost = string_ptbr_tonumber(post)

        outdata.loc[len(outdata),['NumeroSeguidores','NumeroPostagens','@Perfil','url']] = [nflw, npost, profileig , urllink]
    
    else:
        continue

# close bot instagram.
bot.quit()


# start datetime tag file and text dd/mm/YY
today = date.today()
d1 = today.strftime("%d%m%Y")

date_s = today.strftime("%d/%m/%Y") 

fileout = f"lista_{d1}"


order_follow_number = outdata.sort_values('NumeroSeguidores', ascending=False)
# save to file the list. arquived file


order_follow_number.index = pd.RangeIndex(start=1, stop=len(order_follow_number)+1, step=1)

order_follow_number.to_csv(fileout+'.csv')

# save markdown. backup list
order_follow_number.to_markdown(fileout+'.md')


# format list to visualize in markdown file on github. creat a final list (lista_atual.txt) form backup list (lista_DDMMYYYY.md)

with open('lista_atual.md','w') as list_out, open(fileout+'.md') as list_f:

    cab =  f" **Perfis sobre Arquivologia no Instagram** \n\n Lista dos perfis encontratos a partir da pesquisa com os termos 'arquivo', 'arquivologia' e 'arquivística'. \n\n Pesquisa realizada no dia {date_s}.\n\n"
    list_out.write(cab)
    for il in list_f.readlines():
        list_out.write(f'{il}')
    rpe = "\n\n [Informações sobre o projeto 'Perfis sobre Arquivologia no Instagram'](https://github.com/mmacpaulo/ProfilesArchiveInstagram)"
    list_out.write(rpe)

    list_f.close()
    list_out.close()
