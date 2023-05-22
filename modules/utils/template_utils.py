import os
import modules.utils.file_utils as file_utils
import json
from modules.models.api_models import TemplateBaseModel, to_serializable
from datetime import datetime
from config import config

work_dir = config.work_dir
output_dir = config.work_dir
#利用file_util中的方法，获取work_dir下所有文件夹
def get_all_templates_folders():
    folders = file_utils.get_dirs(work_dir)
    return folders

def get_new_template_folder_name():
    folders = get_all_templates_folders()
    i = 1
    while True:
        folder = "template_folder" + str(i)
        if folder not in folders:
            return folder
        i += 1

def get_new_template_name(folder):
    templates = get_templates_from_folder(folder)
    i = 1
    while True:
        template = "template" + str(i)
        if template not in templates:
            return template
        i += 1



def get_title_from_model_name(model_name: str) -> str:
    from modules.data_manager import checkpoints_models
    matching_titles = [model.title for model in checkpoints_models if model.model_name == model_name]

    if matching_titles:
        return matching_titles[0]
    else:
        return None
    
def get_model_name_from_hash(hash:str):
    from modules.data_manager import checkpoints_models
    matching_model_name = [model.model_name for model in checkpoints_models if model.title.endswith(f"[{hash}]")]

    if matching_model_name:
        return matching_model_name[0]
    else:
        return None
    
def get_model_name_from_title(title: str) -> str:
    from modules.data_manager import checkpoints_models
    matching_model_name = [model.model_name for model in checkpoints_models if model.title == title]

    if matching_model_name:
        return matching_model_name[0]
    else:
        return None

#利用file_util中的方法，获取某个template文件夹下所有json文件
def get_templates_from_folder(folder:str):
    templates = file_utils.get_json_files(os.path.join(work_dir, folder))
    return templates

def get_model_from_folder(folder:str, template_name:str):
    all_templates = get_templates_from_folder(folder)
    for template in all_templates:
        if template_name in template:
            return get_model_from_template_path(os.path.join(work_dir, folder, template_name + ".json"))
    return None

#将json先解析成apiTypeModel，根据apiTypeModel中得type再决定解析成哪个model
def get_model_from_template_path(json_file_path:str):
    content = file_utils.read_json_file(json_file_path)
    #json to TemplateBaseModel
    data = json.loads(content)
    apiTypeModel = TemplateBaseModel(**data)
    return apiTypeModel

def get_model_from_template(json):
    #json to TemplateBaseModel
    data = json.loads(json)
    apiTypeModel = TemplateBaseModel(**data)
    return apiTypeModel

def get_input_images_save_path(folder):
    save_path = os.path.join(work_dir, folder, "input_images")
    #获得相对路径
    save_path = os.path.relpath(save_path)
    return save_path

#将apiTypeModel转换成json并存储到template得指定文件夹下
def save_template_model(folder, apiTypeModel:TemplateBaseModel):
    json_file = os.path.join(work_dir, folder, apiTypeModel.template_name + ".json")
    content = json.dumps(apiTypeModel, default= to_serializable, indent=4)
    file_utils.write_json_file(json_file, content)
    
def check_templates_folder_is_exist(folder):
    return folder in get_all_templates_folders()

def check_templates_folder_is_exist(folder, template):
    return template in get_templates_from_folder(folder)

#将apiTypeModel转换成json并存储到template得指定文件夹下
def get_image_save_path(folder):
    current_time = datetime.now()
    # 将时间格式化为指定的字符串形式
    time_folder = current_time.strftime("%Y_%m_%d_%H_%M_%S")
    save_path = os.path.join(output_dir, folder,"output", time_folder)
    return save_path
