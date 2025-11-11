# -*- coding: utf-8 -*-
"""
任务工具模块 - 提供统一的延迟处理、跳转处理和参数定义
"""
import logging
import time
import random
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


def handle_next_step_delay(params: Dict[str, Any], stop_checker=None):
    """处理下一步延迟执行"""
    try:
        if not params.get('enable_next_step_delay', False):
            return
            
        delay_mode = params.get('delay_mode', '固定延迟')
        
        if delay_mode == '固定延迟':
            delay_time = params.get('fixed_delay', 1.0)
            logger.info(f"执行固定延迟: {delay_time} 秒")
            interruptible_sleep(delay_time, stop_checker)
        elif delay_mode == '随机延迟':
            min_delay = params.get('min_delay', 0.5)
            max_delay = params.get('max_delay', 2.0)
            delay_time = random.uniform(min_delay, max_delay)
            logger.info(f"执行随机延迟: {delay_time:.2f} 秒 (范围: {min_delay}-{max_delay})")
            interruptible_sleep(delay_time, stop_checker)
        else:
            logger.warning(f"未知的延迟模式: {delay_mode}")
    except Exception as e:
        logger.error(f"执行下一步延迟时发生错误: {e}")


def interruptible_sleep(duration: float, stop_checker=None):
    """可中断的睡眠函数"""
    if duration <= 0:
        return
    
    start_time = time.time()
    while time.time() - start_time < duration:
        if stop_checker and stop_checker():
            logger.info("延迟被中断")
            break
        time.sleep(0.1)


def handle_success_action(params: Dict[str, Any], card_id: Optional[int], stop_checker=None) -> Tuple[bool, str, Optional[int]]:
    """处理成功动作，包括延迟处理"""
    # 先处理延迟
    handle_next_step_delay(params, stop_checker)
    
    # 然后处理跳转
    action = params.get('on_success', '执行下一步')
    jump_id = params.get('success_jump_target_id')
    
    if action == '跳转到步骤':
        return True, '跳转到步骤', jump_id
    elif action == '停止工作流':
        return True, '停止工作流', None
    elif action == '继续执行本步骤' or action == '继续本步骤':
        return True, '继续执行本步骤', card_id
    else:  # 执行下一步
        return True, '执行下一步', None


def handle_failure_action(params: Dict[str, Any], card_id: Optional[int]) -> Tuple[bool, str, Optional[int]]:
    """处理失败动作"""
    action = params.get('on_failure', '执行下一步')
    jump_id = params.get('failure_jump_target_id')
    
    if action == '跳转到步骤':
        return False, '跳转到步骤', jump_id
    elif action == '停止工作流':
        return False, '停止工作流', None
    elif action == '继续执行本步骤' or action == '继续本步骤':
        return False, '继续执行本步骤', card_id
    else:  # 执行下一步
        return False, '执行下一步', None


def get_standard_next_step_delay_params() -> Dict[str, Dict[str, Any]]:
    """获取标准的下一步延迟参数定义"""
    return {
        "---next_step_delay---": {"type": "separator", "label": "下一步延迟执行"},
        "enable_next_step_delay": {
            "label": "启用下一步延迟执行",
            "type": "bool",
            "default": False,
            "tooltip": "勾选后，执行完当前操作会等待指定时间再执行下一步"
        },
        "delay_mode": {
            "label": "延迟模式",
            "type": "select",
            "options": ["固定延迟", "随机延迟"],
            "default": "固定延迟",
            "tooltip": "选择固定延迟时间还是随机延迟时间",
            "condition": {"param": "enable_next_step_delay", "value": True}
        },
        "fixed_delay": {
            "label": "固定延迟 (秒)",
            "type": "float",
            "default": 1.0,
            "min": 0.1,
            "max": 60.0,
            "decimals": 2,
            "tooltip": "固定延迟的时间（秒）",
            "condition": {"param": "delay_mode", "value": "固定延迟"}
        },
        "min_delay": {
            "label": "最小延迟 (秒)",
            "type": "float",
            "default": 0.5,
            "min": 0.1,
            "max": 60.0,
            "decimals": 2,
            "tooltip": "随机延迟的最小时间（秒）",
            "condition": {"param": "delay_mode", "value": "随机延迟"}
        },
        "max_delay": {
            "label": "最大延迟 (秒)",
            "type": "float",
            "default": 2.0,
            "min": 0.1,
            "max": 60.0,
            "decimals": 2,
            "tooltip": "随机延迟的最大时间（秒）",
            "condition": {"param": "delay_mode", "value": "随机延迟"}
        }
    }


def get_standard_action_params() -> Dict[str, Dict[str, Any]]:
    """获取标准的成功/失败动作参数定义"""
    return {
        "---post_execution---": {"type": "separator", "label": "执行后操作"},
        "on_success": {
            "type": "select",
            "label": "成功时",
            "options": ["执行下一步", "继续执行本步骤", "跳转到步骤", "停止工作流"],
            "default": "执行下一步",
            "tooltip": "当任务执行成功时的操作"
        },
        "success_jump_target_id": {
            "type": "int",
            "label": "成功跳转目标ID",
            "required": False,
            "condition": {"param": "on_success", "value": "跳转到步骤"},
            "tooltip": "任务成功时要跳转到的卡片ID"
        },
        "on_failure": {
            "type": "select",
            "label": "失败时",
            "options": ["执行下一步", "继续执行本步骤", "跳转到步骤", "停止工作流"],
            "default": "执行下一步",
            "tooltip": "当任务执行失败时的操作"
        },
        "failure_jump_target_id": {
            "type": "int",
            "label": "失败跳转目标ID",
            "required": False,
            "condition": {"param": "on_failure", "value": "跳转到步骤"},
            "tooltip": "任务失败时要跳转到的卡片ID"
        }
    }


def merge_params_definitions(*param_defs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """合并多个参数定义字典"""
    merged = {}
    for param_def in param_defs:
        merged.update(param_def)
    return merged


# 兼容性函数，保持与现有代码的兼容
def _handle_next_step_delay(params: Dict[str, Any], stop_checker=None):
    """兼容性函数"""
    return handle_next_step_delay(params, stop_checker)


def _handle_success(action: str, jump_id: Optional[int], card_id: Optional[int]) -> Tuple[bool, str, Optional[int]]:
    """兼容性函数 - 处理成功情况（不包含延迟）"""
    if action == '跳转到步骤':
        return True, '跳转到步骤', jump_id
    elif action == '停止工作流':
        return True, '停止工作流', None
    elif action == '继续执行本步骤' or action == '继续本步骤':
        return True, '继续执行本步骤', card_id
    else:  # 执行下一步
        return True, '执行下一步', None


def _handle_failure(action: str, jump_id: Optional[int], card_id: Optional[int]) -> Tuple[bool, str, Optional[int]]:
    """兼容性函数 - 处理失败情况"""
    if action == '跳转到步骤':
        return False, '跳转到步骤', jump_id
    elif action == '停止工作流':
        return False, '停止工作流', None
    elif action == '继续执行本步骤' or action == '继续本步骤':
        return False, '继续执行本步骤', card_id
    else:  # 执行下一步
        return False, '执行下一步', None
