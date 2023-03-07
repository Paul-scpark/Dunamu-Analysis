import pandas as pd
from bs4 import BeautifulSoup, NavigableString, Tag
from tqdm import tqdm
import requests, csv, time

## 두나무의 핵심 키워드를 뉴스 검색 키워드로 활용하여 데이터 수집하기
keyword_lst = [
    '두나무', '두나무 블록체인', '두나무 NFT', '두나무 메타버스', 
    '두나무 업비트', '두나무 증권플러스', '두나무 비상장', '두나무 맵플러스', '두나무 세컨블록',
    '두나무 ESG', '두나무 인덱스', '두나무 지수', '두나무 UBCI', '두나무 금융', '두나무 환경', '두나무 청년'
]

## 네이버 뉴스의 페이지 별로 뉴스 기사들을 확인하여 a 태그 정보 수집
for query in keyword_lst:
    for idx, start_num in enumerate(tqdm(range(1, 4000, 10))):
        # 위에서 정의했던 여러 키워드를 통해 최신 순서대로 네이버 뉴스의 page 별로 데이터 수집
        url = f'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={query}&sort=1&photo=0&field=0&pd=0&ds=&de=&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:dd,p:all,a:all&start={start_num}'
        
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
                # 각 페이지 별로 접근하여, 뉴스 기사의 제목, 날짜, 본문 데이터를 csv 파일로 저장하기
                news_title = soup.select_one('#title_area > span').text
                news_date = soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span').text.split(' ')[0]
                news_text = soup.select_one('#dic_area').find_all(text=True)
                news_text = ''.join(news_text).replace('\n', '').replace('\t', '').replace('\xa0', ' ').replace('  ', ' ')
                
                news_dic['link'] = a_tag['href']
                news_dic['title'] = news_title
                news_dic['date'] = news_date
                news_dic['text'] = news_text
                
                with open('naver_news.csv', 'a', newline='') as csvfile:
                    fieldnames = ['link', 'title', 'date', 'text']
                    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    csv_writer.writerow(news_dic)
                    
            except: pass
            
        if idx % 10 == 0:
            time.sleep(5)

## 수집한 데이터들 안에서 중복 항목을 제거하고, 최종 데이터 저장
df = pd.read_csv('naver_news.csv', header=None)
df.columns = ['link', 'title', 'date', 'text']
df = df.drop_duplicates('link').reset_index(drop=True)
df.to_csv('new_naver_news.csv', index=False)