#需要设置ip、refreshmodels\controlnet models
#template 的work dir 也需要设置
#然后再提供一些接口，让其他脚本不能够调用，只需要调用这个方法就可以了
from modules.config import config
import modules.utils.template_utils as template_utils
from modules.models.template_models import TemplateModel
from modules.models.api_models import ApiType, Img2ImgModel
import modules.utils.api_utils as api_utils
import modules.data_manager as data_manager

class Styler():
    def __init__(self):
        self.config = config

    #设置template存放的文件夹路径
    def set_work_dir(self, path):
        self.config.set_work_dir(path)

    #设置自动保存输出的路径
    def set_output_dir(self, path):
        self.config.set_work_dir(path)
        
    def set_auto_save(self, save:bool):
        self.config.set_is_auto_save(save)

    def get_all_templates(self):
        res = []
        folders = template_utils.get_all_templates_folders()
        for index, folder in folders:
            temp_templates = template_utils.get_templates_from_folder(folder)
            temp_list:TemplateModel = TemplateModel(title=folder, template_list=temp_templates)
            res.append(temp_list)
        return res
    
    def get_model(self, folderName, template_name, prompt, image_base64):
        model_data = data_manager.get_info_in_template_path(folderName, template_name)

        if prompt:
            model_data.api_model.prompt = prompt + ", " + model_data.api_model.prompt
        
        if model_data.template_type == ApiType.img2img.value and image_base64:
            img2img:Img2ImgModel = model_data.api_model
            img2img.init_images.clear()
            img2img.init_images.append(image_base64)
            img2img.mask=None
            img2img.alwayson_scripts["ControlNet"]["args"]["image"] = image_base64

        return model_data
    
    async def submit(self, folder:str, template_name:str, prompt = "", image_base64 = None):
        model_data = self.get_model(folder,template_name, prompt, image_base64)
        res = await api_utils.submit_once(model_data, folder)
        return res
        