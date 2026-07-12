class AppError(Exception):
    """Base class for controlled application errors returned to API clients."""

    status_code: int = 400
    error_code: str = "APP_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnsupportedFileTypeError(AppError):
    status_code = 415
    error_code = "UNSUPPORTED_FILE_TYPE"


class FileTooLargeError(AppError):
    status_code = 413
    error_code = "FILE_TOO_LARGE"


class EmptyFileError(AppError):
    status_code = 400
    error_code = "EMPTY_FILE"


class InvalidDocumentError(AppError):
    status_code = 400
    error_code = "INVALID_DOCUMENT"


class ExtractionError(AppError):
    status_code = 422
    error_code = "EXTRACTION_FAILED"


class LLMProviderError(AppError):
    status_code = 502
    error_code = "LLM_PROVIDER_ERROR"


class LLMValidationError(AppError):
    status_code = 422
    error_code = "LLM_OUTPUT_INVALID"


class NotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"


class EmbeddingError(AppError):
    status_code = 500
    error_code = "EMBEDDING_ERROR"


class InvalidRequestError(AppError):
    status_code = 400
    error_code = "INVALID_REQUEST"
