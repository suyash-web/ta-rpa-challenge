from RPA.Robocorp.WorkItems import WorkItems
from RPA.Excel.Files import Files, XlsxWorkbook

def get_workitems() -> dict:
    """
    Returns input workitems.
    """
    workitems = WorkItems()
    workitems.get_input_work_item()
    workitem = workitems.get_work_item_variables()
    return workitem

class Excel:
    def __init__(self) -> None:
        self.files = Files()

    def create_excel(self, filepath) -> None:
        """
        Creates the excel file with required heads.
        :param filepath: Path to the excel file.
        """
        workbook = self.files.create_workbook(filepath)
        heads =  [["Title", "Date", "Description", "Picture name", "Count of search phrase", "Contains money"]]
        self.files.set_cell_values("A1", heads)
        self.files.set_styles("A1:F1", bold=True)
        workbook.save(filepath)

    def update_excel(self, filepath: str, values: list) -> None:
        """
        Updates the excel with news data.
        :param filepath: Path to the excel file.
        :param values: List of values to append to the file.
        """
        wb: XlsxWorkbook = self.files.open_workbook(filepath)
        row = wb.find_empty_row()
        for num, value in enumerate(values):
            wb.set_cell_value(row, num+1, value)
        wb.save(filepath)
