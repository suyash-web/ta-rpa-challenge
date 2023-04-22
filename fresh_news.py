from RPA.Browser.Selenium import Selenium
from selenium.common.exceptions import ElementClickInterceptedException
from dateutil.relativedelta import relativedelta
from retry import retry
# from openpyxl import load_workbook
# from openpyxl.worksheet.worksheet import Worksheet
from utilities import create_excel, update_excel
from config import DIRECTORIES
from logger import logger
import datetime
import requests
import re

class NyTimes:
    def __init__(self, workitem: dict) -> None:
        self.browser = Selenium()
        self.phrase: str = workitem["phrase"]
        self.section: str = workitem["section"]
        self.months = workitem["months"]
        self.heads = ["Title", "Date", "Description", "Picture name", "Count of search phrase", "Contains money"]
    
    def get_date(self) -> str:
        """
        Returns a date the number of months prior to the current month.
        :param months: Number of months.
        """
        today = datetime.date.today()
        if int(self.months) == 0 or int(self.months) == 1:
            return today.strftime("%m/%d/%Y")
        three_mon_rel = relativedelta(months=int(self.months))
        req_date = (today - three_mon_rel).strftime("%m/%d/%Y")
        return req_date

    def search_query(self):
        """
        Opens the website and searches for the query.
        """
        self.browser.open_available_browser("https://www.nytimes.com")
        self.browser.maximize_browser_window()
        self.browser.maximize_browser_window()
        self.browser.wait_until_element_is_visible("//button[@data-test-id='search-button']", 10)
        self.browser.click_element("//button[@data-test-id='search-button']")
        self.browser.input_text("//input[@name='query']", self.phrase)
        self.browser.click_element("//button[@type='submit']")
        self.browser.wait_until_element_is_visible("//ol[@data-testid='search-results']", 10)
    
    def set_dates(self) -> None:
        """
        Sets the desired dates in the date field.
        :param months: Number of months priors to the current month.
        """
        start_date = self.get_date()
        end_date = datetime.date.today().strftime("%m/%d/%Y")
        self.browser.click_element_when_visible("//label[text()='Date Range']")
        self.browser.wait_until_element_is_visible("//li[@class='css-guqk22']", 10)
        self.browser.click_element_when_visible("//button[text()='Specific Dates']")
        self.browser.wait_until_element_is_visible("//div[@class='css-79elbk']", 5)
        self.browser.input_text("//input[@data-testid='DateRange-startDate']", start_date)
        self.browser.input_text("//input[@data-testid='DateRange-endDate']", end_date)
        self.browser.press_keys("//input[@data-testid='DateRange-endDate']", "RETURN")

    def set_filters(self) -> None:
        """
        Set the desired filters on the result page.
        """
        self.set_dates()
        self.browser.click_element_when_visible("//label[text()='Section']")
        self.browser.click_element_when_visible(f"//span[text()='{self.section.capitalize()}']")
        self.browser.click_element("//label[text()='Section']")

    def total_news(self) -> int:
        """
        Returns the total number of news present for the current filters.
        """
        self.browser.wait_until_element_is_visible("//p[contains(text(), 'Showing')]", 5)
        news_info = self.browser.get_text("//p[contains(text(), 'Showing')]")
        number_of_news = int(news_info.split()[1])
        return number_of_news
    
    @retry((ElementClickInterceptedException, AssertionError), 5, 5)
    def load_more_news(self) -> None:
        """
        Loads more news
        """
        element = self.browser.get_webelement("//button[text()='Show More']")
        self.browser.driver.execute_script("arguments[0].click();", element)
        self.browser.scroll_element_into_view("//a[@data-testid='search-result-qualtrics-link']")

    @retry((Exception), 5, 5)
    def load_all_news(self) -> None:
        """
        Loads all the news for the given time period.
        """
        self.browser.scroll_element_into_view("//a[@data-testid='search-result-qualtrics-link']")
        while self.browser.is_element_visible("//button[text()='Show More']"):
            self.load_more_news()
        all_news = self.browser.get_webelements("//h4[@class='css-2fgx4k']")
        self.browser.scroll_element_into_view(all_news[0])
    
    def download_picture(self, img_xpath: str, img_path: str) -> None:
        """
        Downlaods the image.
        :param img_xpath: Xpath of the image.
        """
        image_url = self.browser.get_element_attribute(img_xpath, "src")
        image_data = requests.get(image_url).content
        with open(img_path, "wb") as f:
            f.write(image_data)

    def get_count_of_sub_string(self, input_string: str, sub_string: str) -> int:
        """
        Returns count of a query in the input string.
        :param input_string: Input string.
        :param sub_string: Sub string to get the count of.
        """
        for char in ".,;?!‘’":
            input_string = input_string.lower().replace(char, "")
        words = input_string.split()
        result = []
        for i in range(0, len(words), len(sub_string.split())):
            result.append(" ".join(words[i:i+len(sub_string.split())]))
        return result.count(sub_string.lower())

    def is_money_present(self, text: str) -> bool:
        """
        Checks if any amount of money is present in the given text.
        :param text: Input string.
        """
        pattern = r'\$\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:dollars|USD))?\b|\b\d+\s*(?:dollars|USD)\b'
        match = re.findall(pattern, text)
        if match:
            return True
        else:
            return False

    def fetch_news_data(self) -> None:
        """
        Fetches data for all the news.
        """
        create_excel(DIRECTORIES.FILEPATH)
        news_titles = []
        date_elements = self.browser.get_webelements("//span[@class='css-17ubb9w']")
        for index, date_element in enumerate(date_elements):
            date = self.browser.get_text(date_element)
            title = self.browser.get_text(self.browser.get_webelements("//h4[@class='css-2fgx4k']")[index])
            if title not in news_titles:
                news_titles.append(title)
                logger.info(f"Getting data for news title: {title}")
                if self.browser.is_element_visible(f"//h4[text()='{title}']/..//p[@class='css-16nhkrn']"):
                    description = self.browser.get_text(f"//h4[text()='{title}']/..//p[@class='css-16nhkrn']")
                    if description == "":
                        description = "Not available"
                else:
                    description = "Not available"
                img_xpath = f"//div[@class='css-e1lvw9' and a/h4/text()='{title}']/following-sibling::figure[@class='css-tap2ym']/..//div/..//img[@class='css-rq4mmj']"
                if self.browser.is_element_visible(img_xpath):
                    filepath = f"{DIRECTORIES.IMAGE_PATH}/img_{index+1}.png"
                    image_name = filepath.split("/")[-1]
                    self.download_picture(img_xpath, filepath)
                else:
                    image_name = "Not available"
                title_count: int = self.get_count_of_sub_string(title, self.phrase)
                desc_count: int = self.get_count_of_sub_string(title, self.phrase)
                money_present: bool = self.is_money_present(title) or self.is_money_present(description)
                update_excel(
                    title=title,
                    date=date,
                    description=description,
                    filename=image_name,
                    title_count=title_count,
                    desc_count=desc_count,
                    money_present=money_present
                )
