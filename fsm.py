from urllib import request
import requests
import googlemaps
from bs4 import BeautifulSoup
from transitions.extensions import GraphMachine
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from io import BytesIO

class TocMachine(GraphMachine):    
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )
        self.abroad_branch = 0
        self.googleApiKey='AIzaSyCi6YOC0WPf8NolMndYvAQ_K874mnE1Qus'
######################################################################################    
    #common fuctions
    def get_web_page(self, url):
        resp = requests.get(
            url=url,
            cookies={'over18': '1'}
        )
        resp.encoding = 'utf8'
        if resp.status_code != 200:
            print('Invalid url:', resp.url)
            return None
        else:
            return resp.text
    
    def get_articles(self, dom, index):
        soup = BeautifulSoup(dom, 'html.parser')
        if index == 1:
            divs = soup.find_all('tr')
            articles = ''
            for d in divs:
                city = d.find('td', 'laf')
                inform = d.find_all('td')
                if city != None:
                    if city.text.find('(') != -1:
                        articles += '%-*s天氣:%-*s氣溫(℃):%s\n' % ( 6+3*(10 - len(city.text)), city.text, 3*(8 - len(inform[1].text)), inform[1].text, inform[2].text)
                    else:
                        articles += '%-*s天氣:%-*s氣溫(℃):%s\n' % ( 3*(10 - len(city.text)), city.text, 3*(8 - len(inform[1].text)), inform[1].text, inform[2].text)
            return articles
        elif index == 2:
            divs = soup.find_all('tr')
            articles = ''
            for d in divs:
                inform = d.find_all('td')
                if inform:
                    if inform[0].text[0] != '0':
                        articles += '編號:%-*s 台灣時間:%12s \n規模:%6s 深度(km):%6s 位置:%s\n\n' % (3*(6 - len(inform[0].text)), inform[0].text, inform[1].text, inform[4].text, inform[2].text, inform[5].text);
                    else:
                        articles += '編號:%-*s 台灣時間:%12s \n規模:%6s 深度(km):%6s 位置:%s\n\n' % (3*(6 - len(inform[0].text))+len(inform[0].text)+2, inform[0].text, inform[1].text, inform[4].text, inform[2].text, inform[5].text);
            return articles
        elif index == 3:
            divs = soup.find_all('tr')
            counter = 0
            articles = ''
            for d in divs:
                inform = d.find_all('td')
                if inform:
                    if counter == 0:
                        articles += '日期: %-12s' % (inform[1].text)
                    elif counter == 1:
                        articles += '農曆: %-8s\n' % (inform[1].text)
                    elif counter == 2:
                        articles += '節氣: %-5s' % (inform[1].text)
                    elif counter == 3:
                        articles += '俗諺: %-5s' % (inform[1].text)
                    elif counter == 4:
                        articles += '節日: %-5s\n\n' % (inform[1].text)
                counter = counter + 1
            return articles
        elif index == 4:
            divs = soup.find_all('tr')
            return divs[5].find('img')['src']
        elif index == 5:
            article = soup.find('div', 'BoxContentbule').text + '\n' +  soup.find('p').text
            if article:
                return article
        
#####################################################################################
    # initial state
    def print_start_message(self, update):
        update.message.reply_text("你好~ 很高興為您服務")
        return True

    def on_enter_startMessage(self, update):
        update.message.reply_text("需要什麼服務呢？\n" + "(1) 查詢國內氣象\n" + "(2) 查詢國外氣象\n" + "(3) [限手機板] 查詢當地天氣\n" + "(4) 其他")

#######################################################################################
    #  國內氣象
    def search_local(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '1'

    def on_enter_local(self, update):
        update.message.reply_text("需要查詢國內的什麼呢？\n" + "(1) 天氣與氣溫\n" + "(2) 濕度\n" + "(3) 累積雨量\n" + "(4) 返回")

########
    def search_local_weather(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '1'

    def on_enter_localWeather(self, update):
        update.message.reply_text("正在顯示台灣今日的天氣與氣溫，請稍等...")
        data = request.urlopen("http://www.cwb.gov.tw/V7/observe/real/Data/Real_Image.png")
        update.message.reply_photo(data)
        update.message.reply_text("還需要了解更多嗎?\n" + "(1) 了解更多資訊\n" + "(2) 返回查詢國內資訊")

    def more_weather(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '1'

    def on_enter_localWeatherMore(self, update):
        update.message.reply_text('http://www.cwb.gov.tw/V7/observe/')
        self.go_back(update)

#######
    def search_local_humidity(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '2'
    
    def on_enter_localHumidity(self, update):
        update.message.reply_text("正在顯示台灣今日濕度，請稍等...")
        data = request.urlopen("http://www.cwb.gov.tw/V7/observe/real/Data/Real_Humidity.png")
        update.message.reply_photo(data)
        update.message.reply_text("還需要了解更多嗎?\n" + "(1) 了解更多資訊\n" + "(2) 返回查詢國內資訊")

    def more_humidity(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '1'

    def on_enter_localHumidityMore(self, update):
        update.message.reply_text('http://www.cwb.gov.tw/V7/observe/')
        self.go_back(update)
    
########
    def search_local_rain(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '3'

    def on_enter_localRain(self, update):
        update.message.reply_text("正在顯示台灣今日累積雨量，請稍等...")
        data = request.urlopen("http://www.cwb.gov.tw/V7/observe/real/Data/Real_Rain.png")
        update.message.reply_photo(data)
        update.message.reply_text("還需要了解更多嗎?\n" + "(1) 了解更多資訊\n" + "(2) 返回查詢國內資訊")

    def more_rain(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        
        return text == '1'

    def on_enter_localRainMore(self, update):
        update.message.reply_text('http://www.cwb.gov.tw/V7/observe/rainfall/hk.htm')
        self.go_back(update)

##############################################################################################3
    # 國外氣象
    def search_abroad(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '2'

    def on_enter_abroad(self, update):
        if self.abroad_branch != 0:
            update = update.callback_query
            self.abroad_branch = 0
        
        keyboard = [[InlineKeyboardButton("亞洲、大洋洲", callback_data='1')],
                    [InlineKeyboardButton("歐洲、非洲", callback_data='2')],
                    [InlineKeyboardButton("美洲", callback_data='3')],
                    [InlineKeyboardButton("中國大陸", callback_data='4')],
                    [InlineKeyboardButton("返回", callback_data='5')]]
        reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('請選擇要查詢的地區:', reply_markup=reply_markup)
        
########
    def search_asia(self, update):
        return self.abroad_branch == 1
    
    def on_enter_asia(self, update):
        update = update.callback_query
        update.message.reply_text('正在顯示亞洲地區氣候，請稍等...')
        page = self.get_web_page('http://www.cwb.gov.tw/V7/forecast/world/world_aa.htm')
        if page:
            articles = self.get_articles(page, 1)
            update.message.reply_text(articles)

        keyboard = [[InlineKeyboardButton("了解更多資訊", callback_data='6'),
                     InlineKeyboardButton("返回查詢國外資訊", callback_data='7')]]
        reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('還需要了解更多嗎?', reply_markup=reply_markup)
        self.abroad_branch = 0

    def more_asia(self, update):
        return self.abroad_branch == 6

    def on_enter_asiaMore(self, update):
        self.abroad_branch = 0
        update = update.callback_query
        update.message.reply_text('http://www.cwb.gov.tw/V7/forecast/world/world_aa.htm')
        self.go_back(update)

########
    def search_europe(self, update):
        return self.abroad_branch == 2

    def on_enter_europe(self, update):
        update = update.callback_query
        update.message.reply_text('正在顯示歐洲、非洲地區氣候，請稍等...')
        page = self.get_web_page('http://www.cwb.gov.tw/V7/forecast/world/world_ea.htm')
        if page:
            articles = self.get_articles(page, 1)
            update.message.reply_text(articles)

        keyboard = [[InlineKeyboardButton("了解更多資訊", callback_data='6'),
                     InlineKeyboardButton("返回查詢國外資訊", callback_data='7')]]
        reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('還需要了解更多嗎?', reply_markup=reply_markup)
        self.abroad_branch = 0

    def more_europe(self, update):
        return self.abroad_branch == 6

    def on_enter_europeMore(self, update):
        self.abroad_branch = 0
        update = update.callback_query
        update.message.reply_text('http://www.cwb.gov.tw/V7/forecast/world/world_ea.htm')
        self.go_back(update)

########
    def search_usa(self, update):
        return self.abroad_branch == 3

    def on_enter_usa(self, update):
        update = update.callback_query
        update.message.reply_text('正在顯示美洲地區氣候，請稍等...')
        page = self.get_web_page('http://www.cwb.gov.tw/V7/forecast/world/world_am.htm')
        if page:
            articles = self.get_articles(page, 1)
            update.message.reply_text(articles)

        keyboard = [[InlineKeyboardButton("了解更多資訊", callback_data='6'),
                     InlineKeyboardButton("返回查詢國外資訊", callback_data='7')]]
        reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('還需要了解更多嗎?', reply_markup=reply_markup)
        self.abroad_branch = 0

    def more_usa(self, update):
        return self.abroad_branch == 6

    def on_enter_usaMore(self, update):
        self.abroad_branch = 0
        update = update.callback_query
        update.message.reply_text('http://www.cwb.gov.tw/V7/forecast/world/world_am.htm')
        self.go_back(update)

########
    def search_china(self, update):
        return self.abroad_branch == 4

    def on_enter_china(self, update):   
        update = update.callback_query
        update.message.reply_text('正在顯示中國地區氣候，請稍等...')
        page = self.get_web_page('http://www.cwb.gov.tw/V7/forecast/world/world_ch.htm')
        if page:
            articles = self.get_articles(page, 1)
            update.message.reply_text(articles)
         
        keyboard = [[InlineKeyboardButton("了解更多資訊", callback_data='6'),
                     InlineKeyboardButton("返回查詢國外資訊", callback_data='7')]]
        reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('還需要了解更多嗎?', reply_markup=reply_markup)
        self.abroad_branch = 0

    def more_china(self, update):
        return self.abroad_branch == 6

    def on_enter_chinaMore(self, update):
        self.abroad_branch = 0
        update = update.callback_query
        update.message.reply_text('http://www.cwb.gov.tw/V7/forecast/world/world_ch.htm')
        self.go_back(update)

###########################################################################################
    #使用位置搜尋氣象
    def search_location(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        
        return text == '3'

    def on_enter_location(self, update):
        update.message.reply_text("請傳送您的位置 (直接點選[附加]>[location])")
    
    def is_getting_location(self, update):
        if update['message']['location']:
            global lat, lng
            self.lat = update['message']['location']['latitude']
            self.lng = update['message']['location']['longitude']
            return True
        else:
            return False
        
    def on_enter_getLocation(self, update):
        url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + '%.6lf' % self.lat + ',' + '%.6lf' % self.lng + '&key=' + self.googleApiKey
        page = self.get_web_page(url)
        
        page1 = page.split('address_components', len(page))
        page = page1[3]
        
        page1 = page.split('\"long_name\" : \"')
        for i in range (0,len(page1[2])):
            if page1[2][i] == '\"':
                break
        city = page1[2][0:i]
        
        for i in range (0,len(page1[3])):
            if page1[3][i] == '\"':
                break
        region = page1[3][0:i]
        
        url = "https://www.google.com.tw/search?q=" + city + region + '氣象' + '&oq=' + city + region + '氣象' 
        update.message.reply_text(url)
        self.go_back(update)
    
###################################################################################################
    #其他
    def search_others(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '4'

    def on_enter_others(self, update):
        update.message.reply_text("需要什麼服務嗎?\n(1) 地震資訊\n(2) 天文資訊\n(3) 每日科普知識\n(4) 返回")
########
    def search_earthquake(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '1'

    def on_enter_earthquake(self, update):
        update.message.reply_text('正在搜尋地震相關資訊，請稍後...')
        page = self.get_web_page('http://www.cwb.gov.tw//V7/modules/MOD_EC_Home.htm')
        if page:
            articles = self.get_articles(page, 2)
            update.message.reply_text(articles)
        
        update.message.reply_text('還需要了解更多嗎?\n(1) 了解更多相關資訊\n(2) 返回')

    def more_earthquake(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '1'

    def on_enter_earthquakeMore(self, update):
        update.message.reply_text('http://www.cwb.gov.tw/V7/earthquake/')
        self.go_back(update)
########
    def search_astronomy(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '2'

    def on_enter_astronomy(self, update):
        update.message.reply_text('正在搜尋今日天文相關資訊，請稍後...')
        page = self.get_web_page('http://www.cwb.gov.tw/V7/astronomy/')
        if page:
            articles = self.get_articles(page, 3)
            update.message.reply_text(articles)
            update.message.reply_text('今日月相')
            data = request.urlopen("http://www.cwb.gov.tw" + self.get_articles(page, 4))
            update.message.reply_photo(data)
        
        update.message.reply_text('還需要了解更多嗎?\n(1) 了解更多相關資訊\n(2) 返回')

    def more_astronomy(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '1'

    def on_enter_astronomyMore(self, update):
        update.message.reply_text('http://www.cwb.gov.tw/V7/astronomy/')
        self.go_back(update)

########
    def search_knowledge(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '3'

    def on_enter_knowledge(self, update):
        update.message.reply_text('正在搜尋每日科普小知識，請稍後...')
        page = self.get_web_page('http://www.cwb.gov.tw/V7/knowledge/')
        if page:
            articles = self.get_articles(page, 5)
            update.message.reply_text(articles)
        
        self.go_back(update)
###########################################################################################
    #Back edge
    def back_search(self, update):
        if self.abroad_branch == 5:
            return True
        
        if hasattr(update.message ,'text'):
            text = update.message.text
            return text == '4'
        else:
            return False
        
    def on_enter_back(self, update):
        if self.abroad_branch == 5:
            update = update.callback_query
            self.abroad_branch = 0
            
        self.go_back(update)

    def go_back_1(self, update):
         if self.abroad_branch == 7:
            return True
        
         if hasattr(update.message ,'text'):
            text = update.message.text
            return text == '2'

    
    def go_back_2(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '4'

    
    def go_back_3(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text == '2'
##########################################################################################
