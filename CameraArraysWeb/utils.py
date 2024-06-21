"""
@Author  ：Hishallyi
@Date    ：2024/6/21
@Code    : 工具类
"""
import sys
import os
import gxipy as gx
from PIL import Image
import datetime
import time

# 指定Python解释器的搜索路径
notebook_path = os.path.abspath('')
project_root = os.path.dirname(notebook_path)
sys.path.append(project_root)


def print_promotion(message):
    print("")
    print("-------------------------------------------------------------")
    if message is not None:
        print(message)
    print("-------------------------------------------------------------")
    print("")
