from modules.models.api_models import CheckpointModel, TemplateBaseModel, Txt2ImgModel, Img2ImgModel, ApiType
import modules.utils.template_utils as template_utils
import os
import PIL.Image as Image
import modules.utils.api_utils as api_utils
import modules.utils.file_utils as file_utils

samplers_k_diffusion = [
    'Euler a',
    'DPM++ 2M',
    'DPM++ 2S a Karras',
    'DPM++ 2M Karras',
    'DPM++ SDE Karras',
]

# these data is choose by your stable diffusion model
checkpoints_models:list[CheckpointModel] = []

#这个如果需要从sd中获取，需要改controlnet的api代码，降低门槛，直接写死好了，下面是我的model名字
control_net_models:list[str] = []

control_net_modules = [
            "none",

            "canny",
            
            "depth_midas",                  
            "depth_leres",                  
            "depth_zoe",                    

            "lineart",                      
            "lineart_coarse",               
            "lineart_anime",                
            
            "mlsd",                         

            "normal_midas",                 
            "normal_bae",                   

            "openpose",                     
            "openpose_face",                
            "openpose_faceonly",            
            "openpose_hand",                
            "openpose_full",                
            
            "scribble_hed",
            "scribble_pidinet",
            "scribble_xdog",

            "seg_ofcoco",                   
            "seg_ofade20k",                 
            "seg_ufade20k",                 

            "shuffle",

            "softedge_hed",                 
            "softedge_hedsafe",             
            "softedge_pidinet",             
            "softedge_pidisafe",            

            "t2ia_color_grid",
            "t2ia_sketch_pidi",

            "threshold"
        ]

def refresh_checkpoints():
    global checkpoints_models
    checkpoints_models = api_utils.get_models()
    return checkpoints_models != []

def get_txt2img_model(txt2img_prompt, txt2img_negative_prompt, steps, sampler_index, restore_faces, tiling, batch_count, batch_size, cfg_scale, seed, height, width, eta, checkpoint_model):
    return Txt2ImgModel().create(prompt=txt2img_prompt, negative_prompt=txt2img_negative_prompt, 
                        steps=steps, sampler_index=sampler_index, restore_faces=restore_faces, 
                        tiling=tiling, n_iter=batch_count, batch_size=batch_size, cfg_scale=cfg_scale, 
                        seed=seed, height=height, width=width, checkpoint_model=checkpoint_model, eta=eta)

def get_img2img_model(save_path, img2img_prompt, img2img_negative_prompt, restore_faces, tiling, seed, sampler_index, steps, cfg_scale, width, height, batch_size, batch_count, eta, inpaint_full_res, inpaint_full_res_padding, checkpoint_model, img_inpaint:Image, mask_inpaint:Image, mask_blur, inpainting_fill, inpainting_mask_invert, resize_mode, denoising_strength,control_enabled,
                      control_module, control_model, control_weight, control_image, control_mask, control_invert_image, control_resize_mode, control_rgbbgr_mode, 
                      control_lowvram, control_processor_res, control_threshold_a, control_threshold_b, control_guidance_start, control_guidance_end, control_guessmode):
    if img_inpaint is not None:
        if save_path is not None:
            img_save_path = os.path.join(save_path, "init_image.png")
            img_inpaint.save(img_save_path)
        init_image = [img_save_path]
    if mask_inpaint is not None:
        if save_path is not None:
            mask_path = os.path.join(save_path, "init_mask.png")
            mask_inpaint.save(mask_path)
        init_mask = mask_path
    else:
        init_mask = ""
    if control_image is not None:
        if save_path is not None:
            control_image_path = os.path.join(save_path, "control_image.png")
            control_image.save(control_image_path)
        control_image = control_image_path
    if control_mask is not None:
        if save_path is not None:
            control_mask_path = os.path.join(save_path, "control_mask.png")
            control_mask.save(control_mask_path)
        control_mask = control_mask_path
    return Img2ImgModel().create(prompt=img2img_prompt, negative_prompt=img2img_negative_prompt, 
                        restore_faces=restore_faces, tiling=tiling, seed=seed, sampler_index=sampler_index, 
                        steps=steps, cfg_scale=cfg_scale, width=width, height=height, batch_size=batch_size, 
                        n_iter=batch_count, eta=eta, inpaint_full_res=inpaint_full_res, 
                        inpaint_full_res_padding=inpaint_full_res_padding, checkpoint_model=checkpoint_model, 
                        init_image=init_image, init_mask=init_mask, mask_blur=mask_blur, 
                        inpainting_fill=inpainting_fill, inpainting_mask_invert=inpainting_mask_invert,
                        resize_mode=resize_mode, denoising_strength=denoising_strength,
                        control_enabled=control_enabled,control_module=control_module, control_model=control_model, control_weight=control_weight, control_image=control_image, 
                        control_mask=control_mask, control_invert_image=control_invert_image, control_resize_mode=control_resize_mode, control_rgbbgr_mode=control_rgbbgr_mode,
                        control_lowvram=control_lowvram, control_processor_res=control_processor_res, control_threshold_a=control_threshold_a, control_threshold_b=control_threshold_b,
                        control_guidance_start=control_guidance_start, control_guidance_end=control_guidance_end, control_guessmode=control_guessmode)

def get_info_in_template_path(template_path, name):
    if not template_path:
        return "错误的文件夹路径"
    if not name:
        return "错误的文件名"
    temp_data = template_utils.get_model_from_folder(template_path, name)
    return temp_data

def save_parameter(template_path, name, options, template_type_label, *args):
    global choose_folder
    if not template_path:
        template_path = template_utils.get_new_template_folder_name()
    #name none or empty
    if not name:
        name = template_utils.get_new_template_name(template_path)
    base_data:TemplateBaseModel = TemplateBaseModel()
    choose_folder = template_path
    base_data.template_name = name
    base_data.options = options
    base_data.template_type = template_type_label

    if base_data.template_type == ApiType.txt2img.value:
        base_data.api_model = get_txt2img_model(*args)
    elif base_data.template_type == ApiType.img2img.value:
        save_path = template_utils.get_input_images_save_path(choose_folder)
        save_path = os.path.join(save_path, name)
        file_utils.check_folder(save_path)
        base_data.api_model = get_img2img_model(save_path, *args)
    template_utils.save_template_model(choose_folder, base_data)
    print(f"成功存储在{choose_folder}文件夹下的{base_data.template_name}")
    return True

def list_files_with_name(filename):
    res = []
    dirpath = os.path.join(os.getcwd(), "css")
    path = os.path.join(dirpath, filename)
    if os.path.isfile(path):
        res.append(path)

    return res