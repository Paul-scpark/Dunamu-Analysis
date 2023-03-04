import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from tqdm import tqdm
import csv, time

## 네이버 뉴스의 페이지 별로 뉴스 기사들을 확인하여 a 태그 정보 수집
for idx, start_num in enumerate(tqdm(range(1, 200, 10))):
    # '두나무'를 키워드로 하여 최신 순서대로 네이버 뉴스의 page 별로 데이터 수집
    url = f'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%EB%91%90%EB%82%98%EB%AC%B4&sort=1&photo=0&field=0&pd=0&ds=&de=&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:dd,p:all,a:all&start={start_num}'
    
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 뉴스 기사의 링크를 담고 있는 a 태그 정보를 news_lst에 저장
    # 언론사 별로 html 구조가 다르기 때문에, '네이버 뉴스' 항목이 존재하는 기사들만 추리기
    news_lst = soup.select("#main_pack > section > div > div.group_news > ul > li > div > div > div > .info_group > a:nth-child(3)")

    ## 수집한 a 태그 정보들을 하나씩 보면서, 각 뉴스 기사의 제목, 날짜, 본문 데이터를 수집
    for a_tag in news_lst:
        news_dic = {
            'link': '',
            'title': '',
            'date': '',
            'text': ''
        }
        
        response = requests.get(a_tag['href'], headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        try:
            news_title = soup.select_one('#title_area > span').text
            news_date = soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span').text
            news_date = news_date.split(' ')[0]
            news_text = soup.select_one('#dic_area').find_all(text=True)
            news_text = ''.join(news_text).replace('\n', '').replace('\t', '').replace('\xa0', ' ').replace('  ', ' ')
            
            news_dic['link'] = a_tag['href']
            news_dic['title'] = news_title
            news_dic['date'] = news_date
            news_dic['text'] = news_text
            
            with open('naver_news.csv', 'a', newline='') as csvfile: # newline을 통해서 csv 파일에서 자동으로 한 줄씩 띄우는 것을 방지
                fieldnames = ['link', 'title', 'date', 'text']
                csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                csv_writer.writerow(news_dic)
                

        except: pass
        
    if idx % 10 == 0:
        time.sleep(10)