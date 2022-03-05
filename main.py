import requests
import m3u8
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Dest': 'iframe',
  }

def capture():
  url = "https://mdstrm.com/live-stream-playlist/574463697b9817cf0886fc17.m3u8"
  
  # m3u8 master playlist
  response = requests.get(url, headers=headers)

  url = response.text.split()[-1] # url media playlist
  while datetime.now() < end:      
      response = requests.get(url, headers=headers) # m3u8 media playlist  
      
      m3u8_media = m3u8.loads(response.text) 
      regex= re.compile(r'[<>:"/\|*?]') 
      for segment in m3u8_media.segments:
          with open(f"{title} {regex.sub(';',schedule)}.ts", "ab") as f:
              f.write(requests.get(segment.uri, headers=headers).content)
      
      # for segment in m3u8_media.segments:
      #     name= re.search("media.*ts", segment.uri).group()
      #     if not os.path.exists(name):
      #         with open(name, "wb") as f:
      #             f.write(requests.get(segment.uri, headers=headers).content) 
      #     else:
      #         print("File already exists: " + name)    
          
      time.sleep(75)
      
response = requests.get("https://www.caracoltv.com/programacion", headers=headers)

soup = BeautifulSoup(response.text, 'html.parser')

scheduleDay=[]
for index, tr in enumerate(soup.find('tbody').find_all("tr")):
    index+=1    
    scheduleDay.append(tuple([split.strip() for split in tr.find("a").get("title").split("-",1)]))
    
    title= scheduleDay[index-1][0]
    schedule= scheduleDay[index-1][1]
    print(index, title, schedule)

user_input= int(input("\nSeleccione el programa>>>"))

title= scheduleDay[user_input-1][0]
schedule= scheduleDay[user_input-1][1]

day= datetime.now().day
moth= datetime.now().month
year= datetime.now().year
start= datetime.strptime(f'{day}-{moth}-{year} {schedule.split("-")[0]}', '%d-%m-%Y %I:%M%p')
end= datetime.strptime(f'{day}-{moth}-{year} {schedule.split("-")[1]}', '%d-%m-%Y %I:%M%p')

while True:
    if (datetime.now() >= start) and (datetime.now()< end):
        capture()
        break
    elif datetime.now() > end:
        print("El programa ya termino")
        break
    elif datetime.now() < start:        
        difference= start-datetime.now()        
        if difference.days==0:
            print("El programa inicia a las:", start.strftime("%I:%M%p"))
            time.sleep(difference.seconds)
    