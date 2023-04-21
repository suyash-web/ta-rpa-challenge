from RPA.Robocorp.WorkItems import WorkItems
from fresh_news import NyTimes
from logger import logger
import os

class Task:
    def make_dirs(self) -> None:
        """
        Builds required directories.
        """
        if not os.path.exists(os.getcwd()+"/output"):
            os.mkdir(os.getcwd()+"/output")
        if not os.path.exists(os.getcwd()+"/images"):
            os.mkdir(os.getcwd()+"/images")

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
            logger.info(f"Searching query {ny_times.phrase}...")
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
