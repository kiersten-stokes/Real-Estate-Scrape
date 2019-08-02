from datetime import timedelta, date

class House:
    def __init__(self, url, html_soup): 
        self.html_soup = html_soup
        
        self.url = url
        self.address = None
        self.zipcode = None
        self.neighborhood = None
        self.sqft = None
        self.beds = None
        self.baths = None
        self.askingprice = None
        self.year = None
        self.dayslisted = None
        self.elevation = None
        self.treecover = None
        self.MLS = None
        self.salesprice = None
    
    
    def house_data(self):
        container = self.html_soup.find('div', attrs={'data-testid' : 'home-details-summary'})
        if container is not None:
            self.set_address(container)
            self.set_neighborhood(container)
            self.set_sqft_bed_bath(container)
            self.set_askingprice(container)
            
        container = self.html_soup.find('ul', attrs={'data-testid' : 'home-features'})
        if container is not None:
            self.set_days_year(container)
    
        container = self.html_soup.find('div', attrs={'data-testid' : 'nearby-points-and-facts'})
        if container is not None:
            self.set_cover_elevation(container)
        
        container = self.html_soup.find('div', attrs={'data-testid' : 'seo-description-paragraph'})
        if container is not None:
            self.set_MLSid(container)
            
            
    def set_address(self, container):
        addrcont = container.find_all('span')
        if addrcont is None:
            return
    
        self.address = addrcont[0].text
        self.zipcode = addrcont[1].text.replace('"', '').split()[2]
        
    
    def set_neighborhood(self, container):
        nbhdcont = container.find('a', attrs={'class' : 'HomeSummaryShared__NeighborhoodLink-vqaylf-2 kIYmye'})
        if nbhdcont is None:
            return
    
        self.neighborhood = nbhdcont.text
        
        
    def set_sqft_bed_bath(self, container):
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
                self.sqft = item.text.split()[0]
            elif 'Beds' in item.text:
                self.beds = item.text.split()[0]
            elif 'Baths' or 'Bath' in item.text:
                self.baths = item.text.split()[0]
                
    
    def set_askingprice(self, container):  
        pricecont = container.find('h3', attrs={'data-testid' : 'on-market-price-details'})
        if pricecont is None:
            return
        
        self.askingprice = pricecont.text
        
        
    def set_days_year(self, container):
        featcont = container.find_all('li')
        if featcont is None:
            return
        
        for item in featcont:
            if item.text is None:
                break
            elif 'on Trulia' in item.text:
                delta = item.text.split()[0]
                if '<1' in delta:
                    self.dayslisted = date.today()
                elif '+' in delta:
                    self.dayslisted = date.today() - timedelta(days=180)
                else:
                    self.dayslisted = date.today() - timedelta(days=int(delta))
            elif 'Built' in item.text:
                self.year = item.text.split()[2]
    
    
    def set_cover_elevation(self, container):
        tdcontainer = container.find_all('td')
        if tdcontainer is None:
            return
        
        for item in tdcontainer:
            if item.text is None:
                break
            elif 'ft' in item.text:
                self.elevation = item.text.split()[0]
            elif '%' in item.text:
                self.treecover = item.text
    
    
    def set_MLSid(self, container):
        paragraph = container.text
        if paragraph is None:
            return
        
        if 'MLS#' in paragraph:
            index = paragraph.index('MLS#')
            self.MLS = paragraph[index+5:len(paragraph)-1]
        