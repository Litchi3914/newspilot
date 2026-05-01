class LLMError(Exception):
    pass

class MissingAPIKeyError(LLMError):
    pass

class RealCallDisabledError(LLMError):
    pass

class LLMResponseValidationError(LLMError):
    pass
