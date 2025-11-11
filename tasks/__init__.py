#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务模块包初始化文件
导出可用的任务模块列表
"""

import os
import sys
import logging
import importlib
from typing import List, Dict, Any

# 配置日志
logger = logging.getLogger(__name__)

# 保存导入的模块 - 将在文件末尾重新定义为字典格式
_TASK_MODULES_LIST = []

def _init_task_modules():
    """初始化可用的任务模块"""
    global _TASK_MODULES_LIST

    # 确保模块清空
    _TASK_MODULES_LIST = []

    # 预定义的任务模块列表（避免动态扫描目录）
    predefined_modules = [
        'mouse_scroll',
        'delay_task',
        'keyboard_input',
        'find_image_and_click',
        'conditional_control',
        'rotate_view_task',
        'find_color_task',
        'start_task',
        'click_coordinate',
        'ocr_region_recognition',
        'mouse_click_simulation',  # 新增：整合的鼠标操作模块
        'mumu_app_manager'  # 新增：MuMu应用管理模块
    ]

    # 导入每个模块
    for module_name in predefined_modules:
        try:
            # 构建完整的模块名称
            full_module_name = f"tasks.{module_name}"

            # 导入模块
            module = importlib.import_module(full_module_name)

            # 添加到模块列表
            _TASK_MODULES_LIST.append(module)
            # logger.info(f"成功导入任务模块: {module_name}")  # 已禁用，避免日志过多
        except Exception as e:
            logger.error(f"导入任务模块 {module_name} 失败: {str(e)}")

    # 如果导入失败，添加空白模块
    if not _TASK_MODULES_LIST:
        logger.warning("所有任务模块导入失败，将使用空白模块")
        _TASK_MODULES_LIST = [EmptyTaskModule()]

class EmptyTaskModule:
    """空白任务模块，用于在未找到任何有效模块时作为占位符"""
    
    @staticmethod
    def execute_task(**kwargs):
        """执行任务的方法"""
        logger.warning("执行空白任务模块，请确保正确安装任务模块")
        return False, "未找到有效的任务模块"
    
    @staticmethod
    def execute_card(**kwargs):
        """执行卡片的方法"""
        logger.warning("执行空白卡片模块，请确保正确安装任务模块")
        return False, "未找到有效的卡片模块"
    
    @staticmethod
    def run(**kwargs):
        """运行任务的方法"""
        logger.warning("运行空白任务模块，请确保正确安装任务模块")
        return False

# 初始化任务模块
_init_task_modules()

# -*- coding: utf-8 -*-
# 显式导入所有需要的任务模块

# --- 保持和实际模块文件对应的导入 ---
from . import delay_task          # <--- 修改：导入包含 execute_task 的模块
from . import keyboard_input      # 对应 "模拟键盘操作"

# --- 新增的或重命名的模块导入 ---
from . import conditional_control
from . import start_task # <<< ADDED: Import the module directly
from . import ocr_region_recognition # <<< RE-ENABLED: Import ocr_region_recognition module
from . import mouse_click_simulation # <<< ADDED: Import mouse_click_simulation module
from . import find_color_task
from . import ldplayer_app_manager # <<< ADDED: Import ldplayer_app_manager module
from . import mumu_app_manager # <<< ADDED: Import mumu_app_manager module

# -----------------------------------------------------------

# ==================================
#  主要任务注册表 (用于UI显示)
# ==================================
PRIMARY_TASK_MODULES = {
    # 起点任务 - 放在第一位
    "起点": start_task,

    # 鼠标相关操作 - 整合为模拟鼠标操作
    "模拟鼠标操作": mouse_click_simulation,  # <<< RENAMED: 从"模拟鼠标点击"改为"模拟鼠标操作"，整合鼠标滚轮和旋转视角

    # 输入操作
    "模拟键盘操作": keyboard_input,

    # 控制流程
    "延迟": delay_task,
    "条件控制": conditional_control,

    # 图像识别
    "找色功能": find_color_task,
    "OCR文字识别": ocr_region_recognition,

    # 应用管理
    "雷电应用管理": ldplayer_app_manager,
    "MuMu应用管理": mumu_app_manager,
}

# ==================================
#  完整任务注册表 (包含向后兼容映射)
# ==================================
TASK_MODULES_DICT = {
    # 主要任务类型
    **PRIMARY_TASK_MODULES,

    # 向后兼容的旧任务类型（映射到新模块）
    "查找图片并点击": mouse_click_simulation,  # 向后兼容
    "点击指定坐标": mouse_click_simulation,    # 向后兼容
    "鼠标滚轮操作": mouse_click_simulation,    # 向后兼容
    "旋转视角": mouse_click_simulation,        # 向后兼容
    "键盘输入": keyboard_input,               # 向后兼容
}

# ==================================
#  执行器兼容性：提供列表和字典两种格式
# ==================================
# 为了保持向后兼容，TASK_MODULES 可以是字典或列表
# 执行器会自动处理这两种格式
TASK_MODULES = TASK_MODULES_DICT  # 默认使用字典格式

# ==================================
#  通用参数定义 - REMOVED from here
# ==================================
# def get_common_post_execute_params() -> Dict[str, Dict[str, Any]]:
#    ...

# ==================================
#  辅助函数 (可选, 如果UI或其他地方需要)
# ==================================
def get_available_tasks():
    """返回主要任务类型名称列表（用于UI显示）"""
    return list(PRIMARY_TASK_MODULES.keys())

def get_all_tasks():
    """返回所有任务类型名称列表（包含向后兼容）"""
    return list(TASK_MODULES_DICT.keys())

def get_task_module(task_type_name: str):
    """根据任务类型名称获取对应的模块"""
    return TASK_MODULES_DICT.get(task_type_name)