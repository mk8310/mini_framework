import traceback
from typing import Optional, Dict, Any, Union

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import Field, ValidationError
from starlette.responses import JSONResponse

from mini_framework.web.std_models.base_model import BaseViewModel


class ErrorResponse(BaseViewModel):
    error_code: str = Field(..., description="业务相关错误代码")
    message: str = Field(..., description="描述错误的调试信息")
    user_message: Optional[str] = Field(None, description="可显示给用户的用户友好消息")
    details: Union[str, dict, None] = Field(None, description="关于错误的额外详细信息（如果有的话）")
    stack: Optional[str] = Field(None, description="错误堆栈信息")


class MiniHTTPException(HTTPException):
    def __init__(self, status_code: int, error_code: str, detail: str, user_message: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
                 stack: Optional[str] = None):
        """
        自定义HTTP异常
        :param status_code: HTTP status code
        :param error_code: 业务相关错误代码
        :param detail: 错误描述
        :param user_message: 用户友好的错误消息
        :param details: 详细的错误信息
        :param headers: HTTP headers
        :param stack: 错误堆栈信息
        """
        if headers is None:
            headers = {}
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        if stack is not None:
            self.stack = stack
        else:
            self.stack = traceback.format_exc()

        self.error_code = error_code
        self.user_message = user_message
        self.details = details

    @staticmethod
    def from_http_exception(error: HTTPException, headers: Optional[Dict[str, str]] = None):
        if headers is None:
            headers = {}
        headers.update(error.headers)
        error_code = str(error.status_code)
        return MiniHTTPException(
            error.status_code,
            error_code=error_code,
            detail=error.detail,
            stack=traceback.format_exc(),
            details=None,
            headers=headers
        )

    @staticmethod
    def from_exception(e: Exception, headers: Optional[Dict[str, str]] = None):
        return MiniHTTPException(
            status_code=500,
            error_code="500",
            detail=str(e),
            stack=traceback.format_exc(),
            user_message="服务器内部错误",
            headers=headers
        )

    @staticmethod
    def from_validation_error(exc: ValidationError):
        errors = exc.errors()
        return MiniHTTPException(
            status_code=422,
            error_code="VALIDATION_ERROR",
            detail="输入验证失败",
            user_message="输入信息中有一些无效的值",
            details={"fields": errors},
            stack=traceback.format_exc()
        )

    def response(self, headers: Optional[Dict[str, str]] = None):
        if headers is None:
            headers = {}
        headers.update(self.headers)
        err_resp = ErrorResponse(
            error_code=self.error_code,
            message=self.detail,
            user_message=self.user_message,
            details=self.details
        )
        err_resp_detail = jsonable_encoder(err_resp)
        return JSONResponse(
            content=err_resp_detail,
            status_code=self.status_code,
            headers=headers
        )
