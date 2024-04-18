import logging
from time import sleep
from datetime import datetime
from RPA.Excel.Files import Files
from RPA.Browser.Selenium import Selenium
from libraries.utils import *

logger = logging.getLogger(__name__)

SECTIONS = [
    "Any",
    "Arts",
    "Books",
    "Business",
    "Movies",
    "New York",
    "Sports",
    "Style",
    "Travel",
    "U.S."
]

class BrowserActions:
    
    def __init__(self, search_phrase, option = 0, months=0):
        """Initialize the browser actions with search options."""
        self.excel = Files()
        self.excel.create_workbook()
        logging.basicConfig(filename='output/logs.log', level=logging.INFO)
        self.search_phrase = search_phrase
        self.months = get_previous_months(months)
        self.option = SECTIONS[option]
        self.driver = Selenium()
        URL = "https://www.nytimes.com/"
        self.driver.open_available_browser(URL, headless = True, maximized = True)
        logger.info(f"{datetime.now()}: Opened browser and navigated to {URL}.")
        
        
    def select_topic(self):
        """Select a news topic based on the specified option."""
        if self.option != 'Any':
            # wait for tand click dropdown button
            self.driver.wait_until_page_contains_element("css:[data-testid='search-multiselect-button']", timeout=20)
            self.driver.click_button("css:[data-testid='search-multiselect-button']")
            # wait for and collect dropdown options
            self.driver.wait_until_element_is_visible("css:[data-testid='DropdownLabel']", timeout=20)
            options = self.driver.find_elements("css:[data-testid='DropdownLabel']")
            # select dropdown option based on the input option
            for option in options:
                val = self.driver.get_text(option)
                if self.option.lower() in val.lower():
                    self.driver.click_element(option)
                    logger.info(f"{datetime.now()}: Selected topic: {val}.")
                    break
            
        
    def select_sort_by(self):
        """Sort the search results by newest first."""
        try:
            # wait and click sort by dropdown button
            self.driver.click_element_when_clickable("class:css-v7it2b", timeout=20)
            #wait and click sort by newest
            self.driver.click_element_when_clickable("css:[value='newest']", timeout=20)
            logger.info(f"{datetime.now()}: Selected sort by 'newest' successfully.")
        except Exception as e:
            logger.info(f"{datetime.now()}: Could not select 'sort by' with error: {e}.")
            
            
    def navigate_to_search(self):
        """Navigate to the search page and input the search query."""
        # wait and click search button
        sleep(1)
        try:
            self.driver.click_element_when_clickable("css:[data-testid='Reject all-btn']", timeout=20)
        except:
            pass
        self.driver.click_element_when_clickable("css:[data-testid='search-button']", timeout=20)
        #self.driver.click_button("css:[data-testid='search-button']")
        # wait and input search phrase
        self.driver.wait_until_element_is_enabled("css:[data-testid='search-input']", timeout=20)
        self.driver.input_text("css:[data-testid='search-input']", self.search_phrase)
        # submit search phrase by pressing enter
        self.driver.press_keys("css:[data-testid='search-input']", "ENTER")
        self.select_sort_by()
        sleep(1)
        self.select_topic()
        sleep(1)
        logger.info(f"{datetime.now()}: Navigated to search results.")


    def load_more(self):
        """Attempt to load more search results."""
        try:
            # scroll to bottom of page to avoid bot detection
            self.driver.execute_javascript("window.scrollTo(0, document.body.scrollHeight);")
            # wait and click load more button
            self.driver.click_element_when_clickable("css:[data-testid='search-show-more-button']", timeout=20)
        except Exception as e:
            logger.info(f"{datetime.now()}: Could not load more results with error: {e}.")
            
        
    def search(self):
        """Perform the search and process all results according to the specified months."""
        done = 0
        # find all search results up untill the specified months (stop when earlier month is found)
        while 1:
            # wait and gather all search results
            sleep(1)
            self.driver.wait_until_element_is_visible("css:[data-testid='search-bodega-result']", timeout=20)
            cards = self.driver.find_elements("css:[data-testid='search-bodega-result']")
            for i, card in enumerate(cards):
                # get date of each search result
                date_el = self.driver.find_element("css:[data-testid='todays-date']", card)
                date_text = self.driver.get_text(date_el)
                # get month name and year
                month_name_short = date_text.split(' ')[0][:3]
                try:
                    year = str(date_text.split(',')[1])
                except:
                    year = str(datetime.now().year)
                # check if month and year is in requested month and years list
                if (month_name_short, year) not in self.months and 'ago' not in date_text:
                    # break if earlier month found
                    done = 1
                    break
            if done:
                break
            # if not done, load more search results
            self.load_more()
        # initiate results dictionary
        results = {'Title':['Title'], 'Content':['Content'], 'Date':['Date'], 'Phrase Count':['Phrase Count'], 'Has Money':['Has Money'], 'Image':['Image']}
        # wait and gather all search results
        self.driver.wait_until_element_is_visible("css:[data-testid='search-bodega-result']", timeout=20)
        cards = self.driver.find_elements("css:[data-testid='search-bodega-result']")
        
        for i, card in enumerate(cards):
            # get date of each search result
            date_el = self.driver.find_element("css:[data-testid='todays-date']", card)
            date_text = self.driver.get_text(date_el)
            month_name_short = date_text.split(' ')[0][:3]
            try:
                year = str(date_text.split(',')[1])
            except:
                year = str(datetime.now().year)
            # stop processing if earlier month found
            if (month_name_short, year) not in self.months and 'ago' not in date_text:
                done = 1
                break
            # get title, content, image and phrase count of each search result
            title_el = self.driver.find_element("css:[data-testid='search-bodega-result'] h4", card)
            title = self.driver.get_text(title_el)
            try:
                content_el = self.driver.find_element("class:css-16nhkrn", card)
                content = self.driver.get_text(content_el)
            except Exception as e:
                content = ''
                logger.info(f"{datetime.now()}: Could not find conent for {title} with error: {e}.")
            try:
                image_el = self.driver.find_element('tag:img', card)
                image = self.driver.get_element_attribute(image_el, 'src')
                download_path = initialize_directories()
                image_path = download_image(image, download_path)
            except Exception as e:
                # set empty image path if image download fails or no image is found
                image_path = ''
                logger.info(f"{datetime.now()}: Could not download image for {title} with error: {e}.")
            # get count of search phraser in title and content
            phrase_count = str((content + title)).lower().count(self.search_phrase.lower())
            # check if Dollar amount is present in title or content
            _has_money = has_money(str(title) + str(content))
            # append results to dictionary
            results['Title'].append(title)
            results['Content'].append(content)
            results['Date'].append(date_text)
            results['Phrase Count'].append(phrase_count)
            results['Image'].append(image_path)
            results['Has Money'].append(_has_money)
        # append results to Excel worksheet
        self.excel.append_rows_to_worksheet( results)
        logger.info(f"{datetime.now()}: Appended search results to Excel worksheet.")
        

    def save_file(self):
        """Save the Excel file with the collected data."""
        zip_files('images', 'output/images.zip')
        file_name = "output/NY_TIMES_ARTICLES.xlsx"
        self.excel.auto_size_columns("A", "E")
        self.excel.save_workbook(file_name)
        logger.info(f"{datetime.now()}: Saved Excel file as {file_name}.")
    
    
    def close(self):
        """Close all browsers and the Excel file."""
        self.driver.close_all_browsers()
        self.excel.close_workbook()
        logger.info(f"{datetime.now()}: Closed browser and Excel file.")
               
    