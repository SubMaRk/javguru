# -*-coding:utf8;-*-
import requests as rq
from bs4 import BeautifulSoup as bs
from time import sleep as slp
from humanfriendly import format_timespan
import time
import subprocess

# Clear screen function
clear = lambda: subprocess.call('cls||clear', shell=True)

# Start record processing time
begin_time = time.time()

# SSL Cert ciphers and Headers
rq.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

# Get JAV search string from user
print('This script made for scraping JAV information from JAV.GURU into txt file')
print('You can input ID Code, Title name, Actress, Series, Tag and Studio to find them')
print('Note : If you input JAV ID, please add "-" after word for better search\n')
keyword = input('Enter what you want to scraping : ')
print('"Min value" means number of link to skip scraping, if it empty "Min value" = 0\n')
vmin = input('Enter Start Min number : ')
print('"Max value" means number of link for scraping, if it empty "Min value" = 0\n')
vmax = input('Enter Start Max number : ')

# Get excel file name
name = keyword.replace('-','')
if keyword == '':
    filename = 'all.txt'
else:
    filename = name + '.txt'

print('File will saving in',filename)

# Search with user input string
search = "https://jav.guru/?s=" + keyword
print('Searching : ' + keyword)

# Get last pages number
raw = rq.get(search, headers=headers)
soup = bs(raw.content, "html.parser", from_encoding='utf-8')

# Check if result page equal 1; return last = 1 to prevent error
x = soup.select_one(".pages")
if x is None:
    last = 1
else:
    last = soup.select_one(".pages").text.split()[3].replace(',','')
# Min - Max movies to scraping
if vmin == '':
    min = 1
    page = min
    count = 0
else:
    min = int(vmin) // 25
    page = min
    count = page * 25
if vmax == '':
    max = int(last) * 25
else:
    max = vmax
movie = 0
print('Found ' + str(last) + ' page(s)' + ', about ' + str(max) + ' movie(s)')
# Loop scraping data in each pages until it equal last
while page <= int(last):
    start_page = time.time()
    url = 'https://jav.guru/page/'+ str(page) + '?s=' + keyword
    html = rq.get(url, headers=headers)
    data = bs(html.content, 'html.parser', from_encoding='utf-8')
    mains = data.select(".inside-article")
    main = mains[0]
    print('Scraping page(s) : ' + url)
    # Check if have link in anchor tag
    href = main.select_one(".grid1 a")
    if href is None:
        print("Movie(s) not found!")
        break
    # Loop get each link from anchor
    for main in mains:
        start_link = time.time()
        link = main.select_one(".grid1 a")['href']
        get = rq.get(link)
        a = bs(get.content, "html.parser")
        indexs = a.select(".inside-article")
        index = indexs[0]
        print('Scraping movie(s) : ' + link)
        file = open(filename, 'a+', encoding='utf-8')
        # Loop collect information in each movies
        for index in indexs:
            # Check if li tags in infoleft class are not equal 7 and tags are matched 'blog', skip link
            if len(index.select(".infoleft li")) != 7 or index.select(".infoleft li")[3].text.replace('Tags: ','')[:4] == 'blog':
                print("Skip this link, no data to collect")
                movie-=1
                continue
            if count <= int(vmin):
                print('Skip ' + str(count) + ' movie(s)')
                count+=1
                continue
            if count >= int(max):
                break
            # Check if the ID Code exists
            idc = index.select(".infoleft li")[0].getText()
            if idc == '':
                idcode = ''
            else:
                # Get ID Code if exists
                idcode = index.select(".infoleft li")[0].text.split()[2]
            print('ID Code :',idcode)
            # Get title of this movie
            title = index.select_one(".titl").getText()
            print('Title name :',title)
            # Check if the Actress exists
            at = index.select(".infoleft li")[5].getText()
            if at == '':
                ats = ''
            else:
                # Get Actress name if exists
                ats = index.select(".infoleft li")[5].text.replace('Actress: ','')
            print('Actress :',ats)
            # Check if the Tags exists
            tg = index.select(".infoleft li")[3].getText()
            if tg == '':
                tags = ''
            else:
                # Get Tags if exists
                tags = index.select(".infoleft li")[3].text.replace('Tags: ','')
            print('Tags :',tags)
            # Check if Series name exists
            se = index.select(".infoleft li")[4].getText()
            if se == '':
                ses = ''
            else:
                # Get Series name if exists
                ses = index.select(".infoleft li")[4].text.replace('Series: ','')
            print('Series name :',ses)
            # Check if the Series name exists
            st = index.select(".infoleft li")[6].getText()
            if st == '':
                std = ''
            else:
                # Get Studio code if exists
                std = index.select(".infoleft li")[6].text.replace('Studio Label: ','')
            print('Studio :',std)
            # Check if the Release Date exists
            rd = index.select(".infoleft li")[1].getText()
            if rd == '':
                rld = ''
            else:
                # Get Release Date if exists
                rld = index.select(".infoleft li")[1].text.replace('Release Date: ','')
            print('Release Date :',rld)
            # Get image link from this movie
            a = index.select_one(".large-screenimg img")
            img = a['src']
            print('Cover link :',img)
            # Write all to file
            file.write(idcode + '\t' + title + '\t' + ats + '\t' + tags + '\t' + ses + '\t' + std + '\t' + rld + '\t' + img + '\n')
        count+=1
        movie+=1
        print('Scraping completed ' + str(movie) + ' movie(s)')
        end_link = time.time() - start_link
        print("Execution link scraping time :",format_timespan(end_link))
        print('\n')
    print('Scraping completed '+ str(page) + ' of ' + str(last) + ' page(s)' + ', Toltal : ' + str(movie) + ' movie(s)' + ', ' + str(count-movie) + ' link(s) has been skip')
    end_page = time.time() - start_page
    print("Execution page(s) scraping time :",format_timespan(end_page))
    page+=1
    slp(3)
    clear()

# Total execution time
end_time = time.time() - begin_time
print("Total execution time : ", format_timespan(end_time))