import requests
import pandas as panda
from bs4 import BeautifulSoup as soup
import uuid
import time


base_url = 'https://www.trulia.com/LA/Shreveport/'
#base_url = 'https://www.trulia.com/OK/Enid/'
agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
response = requests.get(base_url, headers=agent)
html = soup(response.text, 'html.parser')


# get total number of search result pages and their URLs
page_container = html.find('div', attrs={'class' : 'paginationContainer'})
page_list = page_container.find_all('a', attrs={'class' : 'pvl phm'})
numpages = 0
for page in page_list:
    if page.text.strip() and int(page.text.strip()) > numpages:
        numpages = int(page.text.strip())
print(numpages, ' pages of results')

urls = []
urls.append(base_url)
#for page in range(2, numpages+1):
for page in range(2, 3): 
    urls.append(base_url + str(page) + '_p/')




# get all house links for every page of results (~30 links/page)
links = []
for url in urls:
    response = requests.get(url, headers=agent)
    html_soup = soup(response.text, 'html.parser')
    link_soup = html_soup.find_all('li', attrs={'class' : 'xsCol12Landscape smlCol12 lrgCol8'})
    for item in link_soup:
        links.append('https://www.trulia.com' + item.find('a').attrs['href'])
print(len(links), ' total houses to scrape')
# write links to file in case scraping is interrupted?



def get_address(new_house, container):
    addrcont = container.find_all('span')
    if addrcont is None:
        return

    new_house['address'] = addrcont[0].text
    new_house['zipcode'] = addrcont[1].text.replace('"', '').split()[2]


def get_neighborhood(new_house, container):
    nbhdcont = container.find('a', attrs={'class' : 'HomeSummaryShared__NeighborhoodLink-vqaylf-2 kIYmye'})
    if nbhdcont is None:
        return
    
    new_house['neighborhood'] = nbhdcont.text


def get_sqft_bed_bath(new_house, container):
    ulcont = container.find('ul')
    if ulcont is None:
        return
    
    licont = ulcont.find_all('li')
    if licont is None:
        return
    
    for item in licont:
        if item.text is None:
            break
        elif 'sqft' in item.text:
            new_house['sqft'] = item.text.split()[0]
        elif 'Beds' in item.text:
            new_house['bed'] = item.text.split()[0]
        elif 'Baths' or 'Bath' in item.text:
            new_house['bath'] = item.text.split()[0]


def get_askingprice(new_house, container):  
    pricecont = container.find('h3', attrs={'data-testid' : 'on-market-price-details'})
    if pricecont is None:
        return
    
    new_house['asking price'] = pricecont.text
    
    
def get_days_year(new_house, container):
    featcont = container.find_all('li')
    if featcont is None:
        return
    
    for item in featcont:
        if item.text is None:
            break
        elif 'on Trulia' in item.text:
            new_house['days listed'] = item.text.split()[0]
        elif 'Built' in item.text:
            new_house['year built'] = item.text.split()[2]


def get_cover_elevation(new_house, container):
    tdcontainer = container.find_all('td')
    if tdcontainer is None:
        return
    
    for item in tdcontainer:
        if item.text is None:
            break
        elif 'ft' in item.text:
            new_house['elevation'] = item.text.split()[0]
        elif '%' in item.text:
            new_house['tree cover'] = item.text


def get_MLSid(new_house, container):
    paragraph = container.text
    if paragraph is None:
        return
    
    if 'MLS#' in paragraph:
        index = paragraph.index('MLS#')
        new_house['MLS#'] = paragraph[index+5:len(paragraph)-1]
    

# for every saved link, get all required elements
house_data = {}
start_time = time.time()
house_num = 0

for url in links:
    # create empty house data array
    new_house_data = {}
    
    
    # request page and parse html
    response = requests.get(url, headers=agent)
    html_soup = soup(response.text, 'html.parser')
    
    
    # get address, neighborhood, sqft, beds/baths, and asking price
    html_container = html_soup.find('div', attrs={'data-testid' : 'home-details-summary'})
    if html_container is not None:
        get_address(new_house_data, html_container)
        get_neighborhood(new_house_data, html_container)
        get_sqft_bed_bath(new_house_data, html_container)
        get_askingprice(new_house_data, html_container)
    
    
    # get days on market and year built
    html_container = html_soup.find('ul', attrs={'data-testid' : 'home-features'})
    if html_container is not None:
        get_days_year(new_house_data, html_container)
    
    
    # get tree cover and elevation
    html_container = html_soup.find('div', attrs={'data-testid' : 'nearby-points-and-facts'})
    if html_container is not None:
        get_cover_elevation(new_house_data, html_container)
    
    
    # get MLS id of listing
    html_container = html_soup.find('div', attrs={'data-testid' : 'seo-description-paragraph'})
    if html_container is not None:
        get_MLSid(new_house_data, html_container)
    
    
    # assign ID to house and add data to all house data
    uniqueid = uuid.uuid4().hex[:8]
    house_data[uniqueid] = new_house_data
    
    
    # print elapsed time
    house_num = house_num + 1
    if house_num % 5 == 0:
        print('house: %d' % house_num, '\ttime elapsed: %.2f' % (time.time() - start_time))


# create pandas data frame and print
house_df = panda.DataFrame(house_data).transpose()
#panda.set_option("display.max_columns", 100)
#print(house_df)

house_df.to_pickle('output.pkl')
house_df.to_csv('output.csv', sep=',')


#print(panda.read_pickle('output.pkl'))