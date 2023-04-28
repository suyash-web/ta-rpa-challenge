from fresh_news import NyTimes
from logger import logger
from config import DIRECTORIES
import shutil
import os

class Process:
    def __init__(self, workitems: dict) -> None:
        self.workitems = workitems

    def make_dirs(self) -> None:
        """
        Builds required directories.
        """
        if not os.path.exists(DIRECTORIES.OUTPUT):
            os.mkdir(DIRECTORIES.OUTPUT)
        if not os.path.exists(DIRECTORIES.IMAGE_PATH):
            os.mkdir(DIRECTORIES.IMAGE_PATH)
    
    def run_process(self) -> None:
        """
        Drives the process.
        """
        ny_times = NyTimes(self.workitems)
        try:
            flag = False
            logger.info(f"Searching news for query {ny_times.phrase} and section {ny_times.section} from past {ny_times.months} months...")
            search_status = ny_times.search_query()
            if search_status[0]:
                try:
                    ny_times.set_filters()
                except AssertionError:
                    flag = True
                    logger.info("Terminating the process.")
                if not flag:
                    total_news = ny_times.total_news()
                    logger.info(f"{total_news} news found.")
                    logger.info("Loading all the news...")
                    all_news_loaded = ny_times.load_all_news()
                    logger.info("Fetching news data...")
                    news_fetched = ny_times.fetch_data()
                    if not all_news_loaded:
                        logger.info(f"The website could not load all the news. Data for {news_fetched} news has been fetched.")
                    else:
                        logger.info("All the news has been fetched.")
                    logger.info("Ending the process...")
                    shutil.make_archive(DIRECTORIES.IMAGE_ARCHIVES_PATH, 'zip', DIRECTORIES.IMAGE_PATH)
                    shutil.rmtree(DIRECTORIES.IMAGE_PATH)
            else:
                logger.info(search_status[1])
                logger.info("Terminating the process.")
            ny_times.browser.close_browser()
        except Exception as e:
            ny_times.browser.screenshot(filename="output/error.png")
            raise e

    def start(self) -> None:
        """
        Starts the process.
        """
        self.make_dirs()
        self.run_process()
