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

# UserAgent
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
# SSL Cert ciphers
rq.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"
# Set domain url
base_url = 'https://jav.guru/'
search = '?s='

# Get JAV search string from user
print('This script made for scraping JAV information from JAV.GURU into txt file.')
print('You can input ID Code, Title name, Actress, Series, Tag and Studio to find them; If empty means scraping all')
print('Note : If you input JAV ID, please add "-" after word for better search.\n')
keyword = input('Enter what you want to scraping : ')

# Fetch total result pages
print('\nStart fetching link with keyword :',keyword)
begin_fetch_result_page = time.time()
link = base_url + search + keyword
fetch = rq.get(link, headers=headers)
soup = bs(fetch.content, "html.parser", from_encoding='utf-8')
beginpage = 1
lastpage = soup.select_one(".pages")
if lastpage is None:
    lastpage = 1
else:
    lastpage = soup.select_one(".pages").text.split()[3].replace(',','')
end_fetch_result_page = time.time() - begin_fetch_result_page
print('Found total ' + str(lastpage) + ' page(s)')
print('Execution fetching time :',format_timespan(end_fetch_result_page))

# Fetch page links from all result pages
print('\nStart fetching url ' + link + ' from total ' + str(lastpage) + ' page(s)')
begin_fetch_movie_link = time.time()
page_links = []
movie_links = []
count = movie = skip = 0
for i in range(int(beginpage),int(lastpage)):
    url = ('{}/page/{}{}{}'.format(base_url, i, search, keyword))
    page_links.append(url)

#Fetch movie links from all page links
for link in page_links:
    fetch = rq.get(link, headers=headers)
    soup = bs(fetch.content, "html.parser", from_encoding='utf-8')
    data = soup.select(".grid1 a")
    for i in data:
        url = i['href']
        movie_links.append(url)
end_fetch_movie_link = time.time() - begin_fetch_movie_link
print('Found total '+ str(len(movie_links)) + ' url(s)')
print('Execution fetching time :',format_timespan(end_fetch_movie_link))

# Define file name
name = keyword.replace('-','').replace(' ','')

# Fetch information for movie links
for link in movie_links:
    begin_scraping = time.time()
    print('\nStart scraping :',link)
    fetch = rq.get(link, headers=headers)
    soup = bs(fetch.content, "html.parser", from_encoding='utf-8')
    raw = soup.select(".inside-article")
    data = raw[0]
    numfile = count // 500
    if numfile != 0:
        if keyword == '':
            filename = 'all' + '.' + str(numfile) + '.txt'
        else:
            filename = name + '.' + str(numfile) + '.txt'
    else:
        if keyword == '':
            filename = 'all' + '.' + '0' + '.txt'
        else:
            filename = name + '.' + '0' + '.txt'
    print('All data will saving in',filename)

    # Open file to write data
    file = open(filename, 'a+', encoding='utf-8')
    
    # Collecting information in each movie links
    # Whether check tags in .infoleft are equal 7 and tags are matched 'blog', then skip it
    for data in raw:
        if len(data.select('.infoleft li')) != 7 or data.select('.infoleft li')[3].text.replace('Tags: ','')[:4] == 'blog':
            movie -= 1
            skip += 1
            continue
        # Whether check the ID code is exist
        idc = data.select('.infoleft li')[0].getText()
        if idc == '':
            idcode = 'N/A'
        else:
            idcode = data.select('.infoleft li')[0].text.split()[2]
        # Get title if exist
        title = data.select_one('.titl').getText()
        # Whether check the Actress name is exist
        at = data.select('.infoleft li')[5].getText()
        if at == '':
            actress_name = 'N/A'
        else:
            actress_name = data.select('.infoleft li')[5].text.replace('Actress: ','')
        # Whether check the tags are exist
        tg = data.select('.infoleft li')[3].getText()
        if tg == '':
            tag = 'N/A'
        else:
            tag = data.select('.infoleft li')[3].text.replace('Tags: ','')
        # Whether check series title is exist
        se = data.select('.infoleft li')[4].getText()
        if se == '':
            series_title = 'N/A'
        else:
            series_title = data.select('.infoleft li')[4].text.replace('Series: ','')
        # Whether check studio code is exist
        st = data.select('.infoleft li')[6].getText()
        if st == '':
            studio_code = 'N/A'
        else:
            studio_code = data.select('.infoleft li')[6].text.replace('Studio Label: ','')
        # Whether check release date is exist
        rd = data.select('.infoleft li')[1].getText()
        if rd =='':
            release_date = 'N/A'
        else:
            release_date = data.select('.infoleft li')[1].text.replace('Release Date: ' or '\n','')
        # Get cover image link
        img = data.select_one('.large-screenimg img')
        img_url = img['src']
        # Write all data to file
        file.write(idcode + '\t' + title + '\t' + actress_name + '\t' + tag + '\t' + series_title + '\t' + studio_code + '\t' + release_date + '\t' + img_url + '\n')
        print('ID code : ' + idcode + '\nTitle : ' + title + '\nActress Name : ' + actress_name + '\nTags : ' + tag + '\nSeries Title : ' + series_title + '\nStudio : ' + studio_code + '\nRelease Date : ' + release_date + '\nCover : ' + img_url + '\n')
        count+=1
        print('Save all data from ' + str(count) + ' of ' + str(len(movie_links)) + ' to ' + filename + ' success.')
        end_scraping = time.time() - begin_scraping
        print('Execution fetching time :',format_timespan(end_scraping))

print('\nScraping total movie(s) successful.; Collected total ' + str(count) + ' movie(s), skiped total ' + str(skip) + ' movies(s)')
end_time = time.time() - begin_time
print('Execution fetching time :',format_timespan(end_time))
