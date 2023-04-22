from RPA.Robocorp.WorkItems import WorkItems
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font

def get_workitems() -> dict:
    """
    Returns input workitems.
    """
    workitems = WorkItems()
    workitems.get_input_work_item()
    workitem = workitems.get_work_item_variables()
    return workitem

def create_excel(filepath) -> None:
    """
    Creates the excel file with required heads.
    :param filepath: Path to the excel file.
    """
    heads = ["Title", "Date", "Description", "Picture name", "Count of search phrase", "Contains money"]
    workbook = Workbook()
    workbook.save(filepath)
    wb = load_workbook(filepath)
    sheet: Worksheet = wb.active
    for index, head in enumerate(heads):
        sheet.cell(1, index+1).value = head
        sheet.cell(1, index+1).font = Font(bold=True)
    wb.save(filepath)