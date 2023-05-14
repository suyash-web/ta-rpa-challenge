from RPA.Browser.Selenium import Selenium
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from dateutil.relativedelta import relativedelta
from retry import retry
from utilities import Excel
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
        self.excel = Excel()
    
    def get_start_date(self) -> str:
        """
        Returns a date the number of months prior to the current month.
        """
        current_date = datetime.datetime.now()
        nth_month_prior_date = current_date - relativedelta(months=self.months-1)
        first_day_of_month = nth_month_prior_date.replace(day=1).strftime("%m/%d/%Y")
        return first_day_of_month

    def search_query(self) -> bool:
        """
        Opens the website and searches for the query.
        """
        news_available = True
        message = ""
        if not str(self.months).isnumeric():
            news_available = False
            message = "Month format is not correct."
        else:
            self.browser.open_available_browser("https://www.nytimes.com")
            self.browser.maximize_browser_window()
            self.browser.wait_until_element_is_visible("//button[@data-test-id='search-button']", 10)
            self.browser.click_element("//button[@data-test-id='search-button']")
            self.browser.input_text("//input[@name='query']", self.phrase)
            self.browser.click_element("//button[@type='submit']")
            try:
                self.browser.wait_until_element_is_visible("//ol[@data-testid='search-results']", 30)
            except AssertionError:
                news_available = False
                message = f"No news found for phrase {self.phrase}"
            if self.browser.is_element_visible("//p[text()='Showing 0 results for:']"):
                news_available = False
                message = f"No news found for phrase {self.phrase}"
        return news_available, message
    
    def set_dates(self):
        """
        Sets the desired dates in the date field.
        :param months: Number of months priors to the current month.
        """
        start_date = self.get_start_date()
        end_date = datetime.date.today().strftime("%m/%d/%Y")
        self.browser.click_element_when_visible("//label[text()='Date Range']")
        self.browser.wait_until_element_is_visible("//button[@data-testid='search-date-dropdown-a']/..//div//li", 10)
        self.browser.click_element_when_visible("//button[text()='Specific Dates']")
        self.browser.wait_until_element_is_visible("//div[@data-testid='search-day-picker']/div", 5)
        self.browser.input_text("//input[@data-testid='DateRange-startDate']", start_date)
        self.browser.input_text("//input[@data-testid='DateRange-endDate']", end_date)
        self.browser.press_keys("//input[@data-testid='DateRange-endDate']", "RETURN")

    def set_filters(self) -> None:
        """
        Set the desired filters on the result page.
        """
        self.set_dates()
        self.browser.click_element_when_visible("//label[text()='Section']")
        if self.section == "" or self.section == None:
            self.browser.click_element_when_visible("//span[text()='Any']")
        elif type(self.section) == list:
            for section in self.section:
                if type(section) == str:
                    section: str
                    if len(section.strip()) == 0:
                        self.browser.click_element_when_visible("//span[text()='Any']")
                    else:
                        try:
                            self.browser.click_element_when_visible(f"//span[text()='{section.title()}']")
                        except AssertionError:
                            logger.info(f"Section {section} is not available.")
                            raise AssertionError
                elif section == None:
                    self.browser.click_element_when_visible("//span[text()='Any']")
                else:
                    logger.info(f"Section {section} is not available.")
                    raise AssertionError
        elif type(self.section) == str:
            try:
                self.browser.click_element_when_visible(f"//span[text()='{self.section.title()}']")
            except AssertionError:
                logger.info(f"Section {self.section} is not available.")
                raise AssertionError
        else:
            logger.info(f"Section {section} is not available.")
            raise AssertionError
        self.browser.click_element("//label[text()='Section']")
        self.browser.select_from_list_by_value("//select[@data-testid='SearchForm-sortBy']", "newest")

    def total_news(self) -> int:
        """
        Returns the total number of news present for the current filters.
        """
        self.browser.wait_until_element_is_visible("//p[contains(text(), 'Showing')]", 5)
        news_info: str = self.browser.get_text("//p[contains(text(), 'Showing')]")
        number_of_news = int(news_info.split()[1].replace(",", ""))
        return number_of_news
    
    @retry((ElementClickInterceptedException, AssertionError), 5, 5)
    def load_more_news(self) -> bool:
        """
        Loads more news
        """
        element = self.browser.get_webelement("//button[text()='Show More']")
        self.browser.driver.execute_script("arguments[0].click();", element)

    @retry((Exception), 5, 5)
    def load_all_news(self) -> bool:
        """
        Loads all the news for the given time period. Returns False if all the news are not loaded.
        :param total_news: Total number of news available.
        """
        all_news_loaded = True
        self.browser.scroll_element_into_view("//a[@data-testid='search-result-qualtrics-link']")
        while self.browser.is_element_visible("//button[text()='Show More']"):
            title_elements = self.browser.get_webelements("//li[@data-testid='search-bodega-result']//h4")
            self.load_more_news()
            try:
                self.browser.wait_until_element_is_visible(f"(//li[@data-testid='search-bodega-result']//h4)[{len(title_elements)+1}]", 180)
                self.browser.scroll_element_into_view("//a[@data-testid='go-to-homepage']")
            except (AssertionError, TimeoutException):
                try:
                    self.load_more_news()
                    self.browser.wait_until_element_is_visible(f"(//li[@data-testid='search-bodega-result']//h4)[{len(title_elements)+1}]", 120)
                    self.browser.scroll_element_into_view("//a[@data-testid='go-to-homepage']")
                except (AssertionError, TimeoutException):
                    all_news_loaded = False
                    break
        self.browser.scroll_element_into_view(title_elements[0])
        return all_news_loaded
    
    def download_picture(self, img_xpath: str, img_path: str) -> None:
        """
        Downloads the image.
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
            result.append(' '.join(words[i:i+len(sub_string.split())]))
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

    def get_the_largest_element(self, list_of_strings: list) -> str:
        """
        Returns the element with largest number of characters in a list.
        :param list_of_strings: List with all the string elements.
        """
        max_length = -1
        for element in list_of_strings:
            if len(element) > max_length:
                max_length = len(element)
                result = element
        return result
    
    def fetch_data(self) -> None:
        """
        Fetches the data for all the news.
        """
        self.excel.create_excel(DIRECTORIES.FILEPATH)
        news_titles = []
        title_elements = self.browser.get_webelements("//li[@data-testid='search-bodega-result']//h4")
        img_count = 0
        for index, title_element in enumerate(title_elements):
            date = self.browser.get_text(self.browser.get_webelements("//li[@data-testid='search-bodega-result']/div/span[@data-testid='todays-date']")[index])
            if "m ago" in date or "h ago" in date:
                todays_date = datetime.date.today().strftime("%m/%d/%Y")
                date_obj = datetime.datetime.strptime(todays_date, "%m/%d/%Y")
                date = date_obj.strftime("%B %d, %Y")
            elif "," not in date:
                date = f"{date}, {datetime.datetime.now().year}"
            title: str = self.browser.get_text(title_element)
            if not title in news_titles:
                title: str
                news_titles.append(title)
                logger.info(f"Getting data for news title: {title}")
                news_heading = title
                if "'" in title:
                    title = self.get_the_largest_element(title.split("'"))
                desc_xpath = f"//h4[text()='{title}']/following-sibling::p[1]"
                if self.browser.is_element_visible(desc_xpath):
                    description = self.browser.get_text(desc_xpath)
                if not self.browser.is_element_visible(desc_xpath):
                    description = "Not available"
                img_xpath = f"//div[contains(a/h4/text(), '{title}')]/following-sibling::figure//img"
                if self.browser.is_element_visible(img_xpath):
                    filepath = f"{DIRECTORIES.IMAGE_PATH}/img_{img_count+1}.png"
                    self.download_picture(img_xpath, filepath)
                    image_name = filepath.split("/")[-1]
                    img_count += 1
                else:
                    image_name = "Not available"
                news_data = []
                title_count: int = self.get_count_of_sub_string(news_heading, self.phrase)
                desc_count: int = self.get_count_of_sub_string(description, self.phrase)
                money_present: bool = self.is_money_present(news_heading) or self.is_money_present(description)
                news_data.append(news_heading)
                news_data.append(date)
                news_data.append(description)
                news_data.append(image_name)
                news_data.append(f"Title: {title_count} | Description: {desc_count}")
                news_data.append(money_present)
                self.excel.update_excel(
                    DIRECTORIES.FILEPATH,
                    news_data
                )
        return len(news_titles)
