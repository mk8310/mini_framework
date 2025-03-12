from __future__ import annotations

import importlib
import logging
from types import TracebackType
from typing import Mapping, Type

from mini_framework.context import env
from mini_framework.design_patterns.singleton import singleton
from mini_framework.web.std_models.base_model import BaseViewModel


class SentryConfig(BaseViewModel):
    dsn: str
    level: str="info" # 日志级别, "fatal", "critical", "error", "warning", "info", "debug"
    environment: str

@singleton
class MiniLogger:
    def __init__(self):
        self.__logger = logging.getLogger(env.app_name)
        self.__sentry = None
        self.__load_config()

    def __init_default_logger(self):
        """
        默认日志配置
        :return:
        """
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)
        self.__logger.setLevel(logging.INFO)

    def __load_config(self):
        """
        加载日志配置
        :return:
        :example:
            "log":{
                "sentry": {
                    "dsn": "https://xxxxx@xxxxx/xxxxx",
                    "environment": "production"
                },
                "level": "DEBUG",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                "handlers": [
                    {
                        "type": "stream",
                        "level": "DEBUG",
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    },
                    {
                        "type": "file",
                        "level": "DEBUG",
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        "filename": "app.log",
                        "maxBytes": 1024,
                        "backupCount": 3
                    }
                ]
            }
        """
        from mini_framework.configurations import config_injection
        manager = config_injection.get_config_manager()
        log_config = manager.get_domain_config("log")
        if not log_config:
            self.__init_default_logger()
            self.warning("No log configuration found, use default configuration")
            return
        log_level = log_config.get("level")
        if log_level:
            self.__logger.setLevel(log_level)
        log_format = log_config.get("format")
        if log_format:
            formatter = logging.Formatter(log_format)
            for handler in self.__logger.handlers:
                handler.setFormatter(formatter)

        sentry_config = log_config.get("sentry")
        if sentry_config:
            sentry = SentryConfig(**sentry_config)
            self.__init_sentry(sentry)

    def __init_sentry(self, sentry_config: SentryConfig):
        """
        初始化sentry
        :param sentry_config: sentry配置
        :return:
        """
        try:
            importlib.import_module("sentry_sdk")
        except ImportError:
            self.warning("Sentry not found, please install sentry-sdk")
            self.__sentry = None
            return
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        integration = LoggingIntegration(level=self.__logger.level, event_level=self.__logger.level)
        sentry_sdk.init(
            dsn=sentry_config.dsn,
            integrations=[integration],
            traces_sample_rate=1.0,
            debug=env.debug,
            environment=sentry_config.environment
        )
        msg = sentry_sdk.capture_message("Sentry initialized", level="info")
        self.__sentry = sentry_sdk

    def get_logger(self):
        return self.__logger

    def set_level(self, level: int):
        """
        设置日志级别
        :param level: 日志级别, 分别为: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
        :return:
        """
        self.__logger.setLevel(level)
        return self.__logger

    def info(self, msg, *args, **kwargs):
        """
        输出日志
        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        self.__logger.info(msg, *args, **kwargs)
        if not self.__sentry:
            return
        self.__sentry.capture_message(msg, level="info")

    def debug(self, msg, *args, **kwargs):
        """
        输出调试日志
        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        self.__logger.debug(msg, *args, **kwargs)
        if not self.__sentry:
            return
        self.__sentry.capture_message(msg, level="debug")

    def warning(self, msg, *args, **kwargs):
        """
        输出警告日志
        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        self.__logger.warning(msg, *args, **kwargs)
        if not self.__sentry:
            return
        self.__sentry.capture_message(msg, level="warning")

    def error(self, msg, *args, **kwargs):
        """
        输出错误日志
        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        self.__logger.error(msg, *args, **kwargs)
        if not self.__sentry:
            return
        self.__sentry.capture_message(msg, level="error")

    def critical(self, msg, *args, **kwargs):
        """
        输出严重错误日志
        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        self.__logger.critical(msg, *args, **kwargs)
        if not self.__sentry:
            return
        self.__sentry.capture_message(msg, level="critical")

    def exception(
            self, msg, *args,
            exc_info: None | bool | tuple[Type[BaseException], BaseException, TracebackType | None] | tuple[
                None, None, None] | BaseException = True,
            stack_info: bool = False, stack_level: int = 1,
            extra: Mapping[str, object] | None = None):
        """
        输出异常日志
        :param msg: 异常日志
        :param args: 异常日志参数
        :param exc_info: 是否输出异常日志, 可以传入异常信息元组、异常对象或者布尔值，异常元祖包含异常类型、异常对象和堆栈信息，异常对象包含异常类型和异常对象
        :param stack_info: 是否输出堆栈信息
        :param stack_level: 堆栈信息级别
        :param extra: 额外信息
        :param kwargs: 异常日志参数
        :return:
        """
        self.__logger.exception(
            msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stack_level, extra=extra
        )
        if not self.__sentry:
            return
        self.__sentry.capture_message(msg, level="error")


logger = MiniLogger() #.get_logger()
