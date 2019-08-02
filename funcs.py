import requests
import pandas as pd
from bs4 import BeautifulSoup as soup
import uuid
import time
from random import randint

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


def total_pages_results(url):
    html_soup = soupify(url)
    container = html_soup.find('div', attrs={'class' : 'paginationContainer'})
    page_list = container.find_all('a', attrs={'class' : 'pvl phm'})
    
    return int(page_list[-2].text.strip())


def save_house_links(pages, df_prev_links, name):
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
        save_df(links_new, df_prev_links, name, False)
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



def get_salesprice(container):  
    pricecont = container.find('h3')
    if pricecont is None:
        return
    
    return pricecont.text