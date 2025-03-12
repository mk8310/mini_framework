from __future__ import annotations

from typing import List

from pydantic import Field

from mini_framework.design_patterns.singleton import singleton
from mini_framework.web.std_models.base_model import BaseViewModel


class TaskParams(BaseViewModel):
    """
    任务参数
    """

    code: str  # 参数编码
    name: str  # 参数名称
    param_type: str  # 参数类型
    description: str  # 参数描述
    default: str = None  # 默认值
    required: bool = False  # 是否必填
    choices: List[str] = None  # 选项
    regex: str = None  # 正则表达式


class RetryConfig(BaseViewModel):
    max_attempts: int = Field(..., description="最大重试次数")
    delay: float = Field(..., description="重试延迟时间")
    backoff: float = Field(..., description="重试延迟时间的指数")
    jitter: bool = Field(..., description="是否启用抖动")


class AlertConfig(BaseViewModel):
    email_from: str = Field(..., description="发送邮件的邮箱")
    email_to: list = Field(..., description="接收邮件的邮箱")
    email_smtp_server: str = Field(..., description="SMTP服务器")
    email_smtp_port: int = Field(..., description="SMTP端口")
    sms_api_endpoint: str = Field(..., description="短信API地址")
    sms_api_key: str = Field(..., description="短信API密钥")


@singleton
class TaskServiceConfig:
    def __init__(self):
        from mini_framework.configurations import config_injection

        manager = config_injection.get_config_manager()
        task_service_dict = manager.get_domain_config("task_service")
        if not task_service_dict:
            raise ValueError("task_service configuration is required")
        self.retry = RetryConfig(**task_service_dict.get("retry", {}))
        self.alert = AlertConfig(**task_service_dict.get("alert", {}))
        self.app_id = task_service_dict.get("app_id", None)


task_service_config = TaskServiceConfig()

"""
{
    "task_service": {
        "app_id": "task_service",
        "retry": {
            "max_attempts": 3,
            "delay": 1,
            "backoff": 2,
            "jitter": true
        },
        "alert": {
            "email_from": "",
            "email_to": [],
            "email_smtp_server": "",
            "email_smtp_port": 25,
            "sms_api_endpoint": "",
            "sms_api_key": ""
        },
        "task_types": {
            "test":{
                "code": "test",
                "topic": "test",
                "name": "测试任务",
                "description": "测试任务",
                "params": {
                    "param1": {
                        "code": "param1",
                        "name": "参数1",
                        "param_type": "string",
                        "description": "参数1",
                        "default": "default",
                        "required": true,
                        "choices": ["a", "b", "c"],
                        "regex": "^[a-zA-Z0-9_]*$"
                    }
                },
                "max_retry_count": 3,
                "timeout": 3000,
                "retry_interval": 60,
                "retry_backoff": 1.0,
                "retry_delay": 0,
                "retry_delay_backoff": 1.0,
                "retry_delay_max": 0,
                "retry_delay_max_count": 0,
                "executor_cls_model": "test"
            }
        }
    }
}
"""
