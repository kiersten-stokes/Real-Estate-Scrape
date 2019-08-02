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


# get all house links
df_prev_links = None
if path.exists('links_sold.pkl'):
    df_prev_links = pd.read_pickle('links_sold.pkl')

save_house_links(pages, df_prev_links, 'links_sold')

links = pd.read_pickle('links_sold.pkl')
print(len(links), ' total sold houses to scrape')



# get house data
house_data = {}
df_prev_houses = None
if path.exists('forsale_output.pkl'):
    df_prev_houses = pd.read_pickle('forsale_output.pkl')


# initialize crawl monitors and begin loop
house_num = 0
start_time = time.time()

# loop through and add sale price to recognized homes
# add other data as well?
for index,url in links.iterrows():
    
    if house_num >= 20:
        break
    
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
    
    
    container = html_soup.find('div', attrs={'data-testid' : 'home-details-summary'})
    if entry_exists(url[0], df_prev_houses, 'url'):
        if container is not None:
            df_prev_houses.loc[df_prev_houses['url'] == url[0],'est. sales price'] = get_salesprice(container)
    else:
        new_house = House(url[0], html_soup)
        new_house.house_data()
        
        if container is not None:
            new_house.set_salesprice(container)
        
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