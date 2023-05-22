import httpx
from modules.models.api_models import Txt2ImgModel, Img2ImgModel,CheckpointModel, SubmitFolderModel,TemplateBaseModel,ApiType
import modules.data_manager as data_manager
import modules.utils.file_utils as file_util
import base64
from PIL import Image
import json
import os
from io import BytesIO
import requests
import modules.utils.template_utils as template_utils
import modules.utils.image_utils as image_utils
from modules.config import config

ip = "127.0.0.1:7860"

# ... Txt2ImgModel definition ...
def save_base64_image(base64_data, output_path):
    image_data = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_data))
    image.save(output_path, "JPEG")

def get_models():
    url = f"http://{ip}/sdapi/v1/sd-models"
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        print("Connection refused")
        return []
    if response.status_code == 200:
        result = json.loads(response.text)
        models = [CheckpointModel(**model) for model in result]
        data_manager.checkpoints_models = models
        return models
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        data_manager.checkpoints_models = []
        return []

async def txt2img_post_async(img_name, txt2img_model: Txt2ImgModel, output_folder: str):
    url = f"http://{ip}/sdapi/v1/txt2img"

    data = json.dumps(txt2img_model.dict(), default=lambda o: o.__dict__)

    headers = {
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.post(url, data=data, headers=headers)

        if response.status_code == 200:
            result = json.loads(response.text)

            images = result["images"]
            os.makedirs(output_folder, exist_ok=True)
            image_base64_list = []
            
            for index, image_base64 in enumerate(images):
                if config.is_auto_save:
                    save_name = file_util.get_new_file_name(output_folder, img_name, "jpg",index)
                    image_path = os.path.join(output_folder, save_name)
                    save_base64_image(image_base64, image_path)
                    print(f"Image {index} saved at {image_path}")

                image_base64_list.append(image_base64)
            return True, image_base64_list
        else:
            return False, f"Request failed with status code {response.status_code}: {response.text}"

async def img2img_post_async(img_name, img2img_model: Img2ImgModel, output_folder: str):
    url = f"http://{ip}/sdapi/v1/img2img"

    data = json.dumps(img2img_model.custom_to_dict(), default=lambda o: o.__dict__)

    headers = {
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.post(url, data=data, headers=headers)

        if response.status_code == 200:
            result = json.loads(response.text)

            images = result["images"]
            os.makedirs(output_folder, exist_ok=True)
            image_base64_list = []

            for index, image_base64 in enumerate(images):
                if config.is_auto_save:
                    save_name = file_util.get_new_file_name(output_folder, img_name, "jpg", index)
                    image_path = os.path.join(output_folder, save_name)
                    save_base64_image(image_base64, image_path)
                    print(f"Image {index} saved at {image_path}")

                image_base64_list.append(image_base64)
            return True, image_base64_list
        else:
            return False, print(f"Request failed with status code {response.status_code}: {response.text}")


#可以一次性提交多个模板，多次生成并自动生成比较的grid图片
async def submit_all(submit_list: list[SubmitFolderModel]):
    last_save_path = ""
    for i in range(len(submit_list)):
        if submit_list[i].is_submit:
            times = submit_list[i].submit_times
            folder_name = submit_list[i].submit_folder
            save_path = template_utils.get_image_save_path(folder_name)
            last_save_path = save_path
            image_save_path = os.path.join(save_path, "images")
            grids_save_path = os.path.join(save_path, "grids")
            file_util.check_folder(image_save_path)
            file_util.check_folder(grids_save_path)

            for j in range(times):
                images = []
                image_titles = []
                for submit_template in submit_list[i].submit_items:
                    if submit_template.is_submit:
                        sub_times = submit_template.submit_times
                        template_name = submit_template.submit_template
                        sub_images = []
                        for k in range(sub_times):

                            if submit_template.data.template_type  == ApiType.txt2img.value:
                                save_image_name = f"{template_name}_txt_{j}_{k}"
                                txt2img_model = submit_template.data.api_model
                                is_success, res = await txt2img_post_async(save_image_name, txt2img_model, image_save_path)

                            elif submit_template.data.template_type  == ApiType.img2img.value:
                                save_image_name = f"{template_name}_img_{j}_{k}"
                                img2img_model = submit_template.data.api_model
                                is_success, res = await img2img_post_async(save_image_name, img2img_model, image_save_path)

                            if is_success:    
                                sub_images.append(res)
                            else:
                                return f"提交失败！报错如下：{res}"
                        save_image_name = f"{template_name}_sub_grid_{j}"
                        if len(sub_images) > 1:
                            image = image_utils.merge_images_horizontally(sub_images, 3, os.path.join(grids_save_path, save_image_name))
                            images.append(image)
                        elif len(sub_images) == 1:
                            image_data = base64.b64decode(sub_images[0])
                            image = Image.open(BytesIO(image_data))
                            images.append(image)
                        image_titles.append(template_name)
                if len(images) > 1:
                    save_image_name = f"{folder_name}_grid_{j}"
                    image_utils.save_images_to_grids(images, os.path.join(grids_save_path, save_image_name), image_titles)
    return f"已完成：{last_save_path}"


#一次提交一个模板
async def submit_once(data: TemplateBaseModel,save_folder_name):
    #两个保存路径,每次生成完后会自动保存
    #work_dir/save_folder_name/output/time/grids
    #work_dir/save_folder_name/output/time/images
    save_path = template_utils.get_image_save_path(save_folder_name)
    image_save_path = os.path.join(save_path, "images")
    grids_save_path = os.path.join(save_path, "grids")
    file_util.check_folder(image_save_path)
    file_util.check_folder(grids_save_path)

    template_name = data.template_name
    sub_images = []
    if data.template_type  == ApiType.txt2img.value:
        save_image_name = f"{template_name}_txt"
        txt2img_model = data.api_model
        is_success, res = await txt2img_post_async(save_image_name, txt2img_model, image_save_path)

    elif data.template_type  == ApiType.img2img.value:
        save_image_name = f"{template_name}_img"
        img2img_model = data.api_model
        is_success, res = await img2img_post_async(save_image_name, img2img_model, image_save_path)

    if is_success:
        for index, image_base64 in enumerate(res):
            sub_images.append(image_base64)
    else:
        return f"提交失败！报错如下：{res}"
    save_image_name = f"{template_name}_sub_grid"
    if len(sub_images) > 1:
        grid_image = image_utils.merge_images_horizontally(sub_images, 3, os.path.join(grids_save_path, save_image_name))
    return sub_images, grid_image