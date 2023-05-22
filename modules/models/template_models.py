from pydantic import BaseModel
from typing import List

class TemplateModel(BaseModel):
    title: str #folder_name
    template_list: List[str] = [] #该文件夹下所有的template名字
