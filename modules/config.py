import os
from dotenv import load_dotenv
from utils.file_utils import check_folder

# Load environment variables from .env file
load_dotenv()

class Config():
    def __init__(self):
        self.ip = os.getenv('IP', "127.0.0.1:7860")
        self.is_auto_save = True
        self.is_auto_save = os.getenv('IS_AUTO_SAVE')
        save_name = os.getenv('WORK_DIR', "templates")
        outputs_name = os.getenv('OUTPUT_DIR', "outputs")

        #根目录
        self.project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        work_temp_dir = os.path.join(self.project_dir, save_name)
        check_folder(work_temp_dir)
        self.work_dir = work_temp_dir

        output_temp_dir = os.path.join(self.project_dir, outputs_name)
        check_folder(output_temp_dir)
        self.output_dir = output_temp_dir

    def set_is_auto_save(self, value: bool):
        self.is_auto_save = value
    
    def set_ip(self, value: str):
        self.ip = value

    def set_work_dir(self, folder_name: str):
        work_temp_dir = os.path.join(self.project_dir, folder_name)
        check_folder(work_temp_dir)

        self.work_dir = work_temp_dir

    def set_outputs_dir(self, folder_name: str):
        output_temp_dir = os.path.join(self.project_dir, folder_name)
        check_folder(output_temp_dir)

        self.output_dir = output_temp_dir

config = Config()