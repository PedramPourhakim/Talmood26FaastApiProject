from fastapi.responses import JSONResponse
from fastapi import status
from abc import ABC, abstractmethod


class ExceptionResponseSchema(ABC):
    def __init__(self):
        self.error_response = {
            "error" : True,
            "status_code" : status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message" : "Internal Server Error",
            "data" : ""
        }

    @abstractmethod
    def handle_exception(self, exception):
        pass

class HttpExceptionHandler(ExceptionResponseSchema):
    def handle_exception(self, exception):
        self.error_response["status_code"] = exception.status_code
        self.error_response["message"] = str(exception.detail)
        return JSONResponse(status_code=self.error_response["status_code"],
                            content=self.error_response)

class ValidationExceptionHandler(ExceptionResponseSchema):
    def handle_exception(self, exception):
        self.error_response["status_code"] = status.HTTP_422_UNPROCESSABLE_CONTENT
        self.error_response["message"] = "There was a problem with your form request"
        self.error_response["data"] = exception.errors()
        return JSONResponse(
            status_code=self.error_response["status_code"], content=self.error_response
        )