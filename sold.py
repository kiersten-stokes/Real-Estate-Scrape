from os import path
from House import House
from funcs import *


base_url = 'https://www.trulia.com/sold/Shreveport,LA/3_srl/'


# get search result pages
numpages = total_pages_results(base_url)
print(numpages, ' pages of search results to scrape')

pages = [base_url]
#for page in range(2, 3):
for page in range(2, numpages+1):
    pages.append(base_url + str(page) + '_p/')


links = []
save_house_links(links, pages, None)


# get house data
house_data = {}
df_prev_houses = None
if path.exists('forsale_output.pkl'):
    df_prev_houses = pd.read_pickle('forsale_output.pkl')


print('Beginning scrape of ', len(links), ' sold houses')


# initialize crawl monitors and begin loop
house_new = 0
house_append = 0
start_time = time.time()
for url in links:
    
    '''if house_new + house_append >= 40:
        break'''
     
    html_soup = soupify(url)
    
    container = html_soup.find('title')
    if container is not None and 'Access to this page has been denied' in container.text:
        print('Access to page denied, sleeping for 30 minutes')
        links.append(url)
        time.sleep(1800)
        print('Resuming scrape')
        continue
    
    
    container = html_soup.find('div', attrs={'data-testid' : 'home-details-summary'})
    if entry_exists(url, df_prev_houses, 'url'):
        if container is not None:
            df_prev_houses.loc[df_prev_houses['url'] == url,'est. sales price'] = get_salesprice(container)
        house_append = house_append + 1
    else:
        new_house = House(url, html_soup)
        new_house.house_data()
        
        if container is not None:
            new_house.set_salesprice(container)
        
        add_house(house_data, new_house)
        house_new = house_new + 1

    # count house, print elapsed time and save
    if (house_new + house_append) % 10 == 0:
        print('house: %d' % house_new + house_append, '\ttime elapsed: %.2fs' % (time.time() - start_time))
        save_df(house_data, df_prev_houses, 'forsale_output', True)
    
    # sleep to prevent server ban
    time.sleep(randint(2,8))


save_df(house_data, df_prev_houses, 'forsale_output', True)
print('Scraping session complete. ', house_new, ' new houses added and ', house_append, ' houses appended to')