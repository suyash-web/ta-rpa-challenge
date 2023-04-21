import os

if not os.path.exists(os.getcwd()+"/output"):
    os.mkdir(os.getcwd()+"/output")
if not os.path.exists(os.getcwd()+"/images"):
    os.mkdir(os.getcwd()+"/images")

FILEPATH = os.getcwd()+"/output/Fresh News.xlsx"
IMAGE_PATH = os.getcwd()+"/images"