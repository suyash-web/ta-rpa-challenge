from RPA.Robocorp.WorkItems import WorkItems
from fresh_news import NyTimes
from logger import logger
from config import DIRECTORIES
import os

class Task:
    def make_dirs(self) -> None:
        """
        Builds required directories.
        """
        if not os.path.exists(DIRECTORIES.OUTPUT):
            os.mkdir(DIRECTORIES.OUTPUT)
        if not os.path.exists(DIRECTORIES.IMAGE_PATH):
            os.mkdir(DIRECTORIES.IMAGE_PATH)

    def get_workitems(self) -> dict:
        """
        Returns input workitems.
        """
        workitems = WorkItems()
        workitems.get_input_work_item()
        workitem = workitems.get_work_item_variables()
        return workitem
    
    def run_process(self) -> None:
        """
        Drives the process.
        """
        ny_times = NyTimes(workitem=self.get_workitems())
        try:
            flag = False
            logger.info(f"Searching news for query '{ny_times.phrase}' and section '{ny_times.section}' for past {ny_times.months} months...")
            ny_times.search_query()
            try:
                ny_times.set_filters()
            except AssertionError:
                flag = True
                logger.info(f"Section {ny_times.section} is not available.")
            if not flag:
                ny_times.load_all_news()
                ny_times.fetch_data()
                logger.info("All the news has been fetched.")
            ny_times.browser.close_browser()
        except Exception as e:
            ny_times.browser.screenshot(filename="output/error.png")
            raise e

if __name__ == "__main__":
    _task = Task()
    _task.make_dirs()
    _task.run_process()
