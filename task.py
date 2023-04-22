from utilities import get_workitems
from process import Process
from logger import logger

def task():
    """
    Starting point of the process.
    """
    workitems = get_workitems()
    process = Process(workitems=workitems)
    process.start()

if __name__ == "__main__":
    logger.info("Starting the process...")
    task()
    logger.info("Done.")