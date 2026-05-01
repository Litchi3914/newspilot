from src.api.schemas.errors import ErrorCode, APIError


def test_error_codes_exist_and_unique():
    vals = [x.value for x in ErrorCode]
    assert len(vals) == len(set(vals))
    expected = {
        'INVALID_INPUT','PIPELINE_FAILED','RETRIEVER_NOT_FOUND','RETRIEVAL_FAILED','RULE_CHECK_FAILED',
        'LLM_DISABLED','LLM_CALL_FAILED','LLM_SCHEMA_INVALID','DIFF_FAILED','OUTPUT_SCHEMA_INVALID','UNKNOWN_ERROR'
    }
    assert expected.issubset(set(vals))


def test_error_struct_fields():
    e = APIError(code=ErrorCode.UNKNOWN_ERROR, message='x', stage='api', recoverable=False)
    assert e.code == ErrorCode.UNKNOWN_ERROR
    assert e.recoverable is False
