from RPA.Robocorp.WorkItems import WorkItems
from libraries.browser_actions import BrowserActions
    
if __name__ == '__main__':
    # Initialize the WorkItems object
    wi = WorkItems()
    # Access input data (assuming JSON format for work items)
    wi.get_input_work_item()
    browser = BrowserActions(wi.get_work_item_variable("search_phrase"), wi.get_work_item_variable("section"), wi.get_work_item_variable("months"))
    try:
        browser.navigate_to_search()
        browser.search()
        browser.save_file()
    finally:
        browser.close()    
    