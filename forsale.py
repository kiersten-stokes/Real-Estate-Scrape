import requests
import pandas as pd
from bs4 import BeautifulSoup as soup
import uuid
import time
from random import randint
from os import path
from House import House


# change base_url and agents if desired
base_url = 'https://www.trulia.com/LA/Shreveport/'
agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}


def entry_exists(new_entry, df_prev, selector):
    if df_prev is not None:
        this_entry = df_prev.loc[df_prev[selector] == new_entry]
        if this_entry.empty == False:
            return True
    return False


def save_df(data, df_prev, name, transpose):
    df = pd.DataFrame(data)
    if transpose == True:
        df = df.transpose()
    
    df_concat = pd.concat([df_prev, df], sort=False)
    
    df_concat.to_pickle(name + '.pkl')
    df_concat.to_csv(name + '.csv', sep=',')
    
    time.sleep(randint(2,8))


def soupify(url):
    try:
        response = requests.get(url, headers=agent)
        return soup(response.text, 'html.parser')
    except requests.ConnectionError as e:
        print("Connection error")
        print(str(e))
    except requests.Timeout as e:
        print("Timeout error")
        print(str(e))
    except requests.RequestException as e:
        print("General error")
        print(str(e)) 

    return None


def total_pages_results():
    html_soup = soupify(base_url)
    container = html_soup.find('div', attrs={'class' : 'paginationContainer'})
    page_list = container.find_all('a', attrs={'class' : 'pvl phm'})
    
    return int(page_list[-2].text.strip())


def save_house_links(pages, df_prev_links):
    links_new = []
    for page in pages:
        html_soup = soupify(page)
        if html_soup is None:
            continue

        link_soup = html_soup.find_all('li', attrs={'class' : 'xsCol12Landscape smlCol12 lrgCol8'})
        for item in link_soup:
            link = 'https://www.trulia.com' + item.find('a').attrs['href']
            if entry_exists(link, df_prev_links, 0):
                continue
            
            links_new.append(link)
        save_df(links_new, df_prev_links, 'links', False)
    print(len(links_new), ' new links to scrape')
    
    
def add_house(house_data, new_house):
    house_data[uuid.uuid4().hex[:8]] = {'url' : new_house.url, 
                                       'address' : new_house.address,
                                       'zipcode' : new_house.zipcode,
                                       'neighborhood' : new_house.neighborhood,
                                       'sqft' : new_house.sqft,
                                       'beds' : new_house.beds,
                                       'baths' : new_house.baths,
                                       'asking price' : new_house.askingprice,
                                       'year built' : new_house.year,
                                       'list date' : new_house.dayslisted,
                                       'elevation' : new_house.elevation,
                                       'tree cover' : new_house.treecover,
                                       'MLS#' : new_house.MLS,
                                       'est. sales price' : new_house.salesprice
                                      }



# get search result pages
numpages = total_pages_results()
print(numpages, ' pages of search results to scrape')

pages = [base_url]
#for page in range(2, numpages+1):
for page in range(2, 3):
    pages.append(base_url + str(page) + '_p/')


# get all house links
df_prev_links = None
if path.exists('links.pkl'):
    df_prev_links = pd.read_pickle('links.pkl')

save_house_links(pages, df_prev_links)

links = pd.read_pickle('links.pkl')
print(len(links), ' total houses to scrape')



# get house data
house_data = {}
df_prev_houses = None
if path.exists('forsale_output.pkl'):
    df_prev_houses = pd.read_pickle('forsale_output.pkl')


# initialize crawl monitors and begin loop
house_num = 0
start_time = time.time()
for index,url in links.iterrows():
    
    if house_num >= 2:
        break
    
    if entry_exists(url[0], df_prev_houses, 'url'):
        continue
    
    html_soup = soupify(url[0])
    if html_soup is None:
        print('does this ever happen?')
        continue
    
    container = html_soup.find('title')
    if container is not None and 'Access to this page has been denied' in container.text:
        print('Access to page denied, skipping house and sleeping for 1 minute')
        time.sleep(60)
        print('Resuming scrape')
        continue
    
   
    new_house = House(url[0], html_soup)
    new_house.house_data()
    
    add_house(house_data, new_house)

    # count house, print elapsed time and save
    house_num = house_num + 1
    if house_num % 10 == 0:
        print('house: %d' % house_num, '\ttime elapsed: %.2fs' % (time.time() - start_time))
        save_df(house_data, df_prev_houses, 'forsale_output', True)
    
    # sleep to prevent server ban
    time.sleep(randint(2,8))


save_df(house_data, df_prev_houses, 'forsale_output', True)
print('Scraping session complete. ', house_num, ' new houses added')