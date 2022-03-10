
import requests
import m3u8
import time
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from src.win10toast.win10toast import ToastNotifier # pip install -e git+https://github.com/Charnelx/Windows-10-Toast-Notifications.git#egg=win10toast
from searcher import searcherYouTube

toaster = ToastNotifier()
   
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

def get_quality(data,user_input):
    quality={    
        1: "1280x720",
        2: "854x480",
        3: "426x240",
        
    }
    for play in data.playlists:
        resolution= "x".join(str(item) for item in play.stream_info.resolution)
        if resolution == quality[user_input]:
            return (play.uri,resolution)
    return (data.playlists[-1].uri, "best")      
def capture():
    url = "https://mdstrm.com/live-stream-playlist/574463697b9817cf0886fc17.m3u8"

    # m3u8 master playlist
    response = requests.get(url, headers=headers)

    
    data= m3u8.loads(response.text)    
            
    url,resolution = get_quality(data,user_input) # url media playlist
    day= datetime.now().strftime("%d-%m-%y")
    start= datetime.now().strftime('%I%M%p')  
    
    filename= f"{title} {day}_{start}-{end.strftime('%I%M%p')}_{resolution}.ts"
    
    print("Downloading...", filename)
    while datetime.now() < (end + timedelta(minutes=10)):      
        response = requests.get(url, headers=headers) # m3u8 media playlist  

        m3u8_media = m3u8.loads(response.text) 
        for segment in m3u8_media.segments:
            with open(filename, "ab") as f:
                f.write(requests.get(segment.uri, headers=headers).content)
        time.sleep(75)
        
response = requests.get("https://www.caracoltv.com/programacion", headers=headers)

# Captura la programación del día
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


print("\n\n*Calidad de la captura:")
print("1. Alta\n2. Media\n3. Baja")
user_input= (int(input("\n>>>")))

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
            time.sleep(difference.seconds+2)


while True:
    if searcherYouTube():
        while True:
            toaster.show_toast("!Desafío The Box!", "El capítulo se descargo!",
                               duration=5,
                               callback_on_click=exit)
    time.sleep(300) # 5 minutos                