from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options



# Create a new instance of the Chrome options
options = Options()

# Define a user agent string. This should be a string that represents a real browser
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"

# Set the user agent as an argument to options
options.add_argument(f"user-agent={user_agent}")


options.set_capability('pageLoadStrategy', 'none') 

# Dictionary mapping month names to numbers
month_to_number = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}




def get_previous_months(n=0):
    n = max(n, 1)
    
    current_date = datetime.now()
    
    months = []
    
    for i in range(n):
        
        months.append((current_date.strftime('%B'), current_date.year))
        
        if current_date.month == 1:
            current_date = current_date.replace(month=12, year=current_date.year-1)
        else:
            current_date = current_date.replace(month=current_date.month-1)
    
    return months


driver = webdriver.Chrome(options = options)
driver.get("https://apnews.com/search?q=trump&s=3&p=1")




search_phrase = 'trump'
class Post:
    
    def __init__(self, title, content, date, image ):
        self.title = title
        self.content = content
        self.date = date
        self.image = image
        

months = get_previous_months(2)
        
posts = []     
page = 1

while 1:

    driver.get(f"https://apnews.com/search?q=trump&s=3&p={page}")
    page+=1
    
    try:
        btn = driver.find_element(By.CLASS_NAME, "bx-close")
        btn.click()
    except:
        pass
    
    
    try:
        cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "PageList-items-item"))
        )
    except:
        print('no cards')
        break
        
    for card in cards:

        try:

            image = card.find_element(By.TAG_NAME, "img")

            date = card.find_element(By.CLASS_NAME, "PagePromo-date").text
            
            month = date.split(',')[1].split(' ')[1]
            year = int(date.split(' ')[-1])
            
            if (month, year) not in months:
                continue
            
            title = card.find_element(By.CLASS_NAME, "PagePromo-title").text

            content = card.find_element(By.CLASS_NAME, "PagePromo-description").text

            phrase_count = str((content + title)).lower().count(search_phrase.lower()) 
            
            print(title)
            print(content)
            print(phrase_count)

            posts.append(Post(title = title, content = content, date = date, image = image))

        except Exception as e:

            print('some elements were not found')

    
    
    
    