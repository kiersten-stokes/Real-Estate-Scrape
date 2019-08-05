from os import path
from House import House
from funcs import *


# change base_url if desired
base_url = 'https://www.trulia.com/LA/Shreveport/'

# get house data
house_data = {}
df_prev_houses = None
if path.exists('forsale_output.pkl'):
    df_prev_houses = pd.read_pickle('forsale_output.pkl')

# get search result pages
numpages = total_pages_results(base_url)
print(numpages, ' pages of search results to scrape')

pages = [base_url]
for page in range(2, numpages+1):
    pages.append(base_url + str(page) + '_p/')

links = []
save_house_links(links, pages, df_prev_houses)


print('Beginning scrape of ', len(links), ' new houses')
house_num = 0
start_time = time.time()
for url in links:
    
    html_soup = soupify(url)
       
    container = html_soup.find('title')
    if container is not None and 'Access to this page has been denied' in container.text:
        print('Access to page denied, sleeping for 30 minutes')
        links.append(url)
        time.sleep(1800)
        print('Resuming scrape')
        continue
    
   
    new_house = House(url, html_soup)
    new_house.house_data()
    
    add_house(house_data, new_house)

    # count house, print elapsed time and save
    house_num = house_num + 1
    if house_num % 10 == 0:
        print('house: %d' % house_num, '\ttime elapsed: %.2fs' % (time.time() - start_time))
        save_df(house_data, df_prev_houses, 'forsale_output', True)
    
    time.sleep(randint(2,8))
    
save_df(house_data, df_prev_houses, 'forsale_output', True)
print('Scraping session complete. ', house_num, ' new houses added')