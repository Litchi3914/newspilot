import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


def run_cmd(cmd: list[str], name: str):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if p.returncode != 0:
        print(f'[FAIL] {name}')
        print(p.stdout)
        print(p.stderr)
        return False
    print(f'[PASS] {name}')
    return True


def main() -> int:
    checks = []
    checks.append(run_cmd([sys.executable, '-m', 'compileall', 'src', 'scripts', 'tests'], 'compile'))
    checks.append(run_cmd([sys.executable, 'scripts/run_llm_demo.py', '--input', 'data/demo_inputs/sample_article.txt', '--provider', 'mock'], 'llm_demo_mock'))
    checks.append(run_cmd([sys.executable, 'scripts/run_review_demo.py', '--input', 'examples/sample_draft.txt', '--retriever', 'bm25'], 'review_demo'))

    try:
        import importlib
        importlib.import_module('src.api.app')
        print('[PASS] fastapi_app_import')
        checks.append(True)
    except Exception as exc:  # noqa: BLE001
        print('[FAIL] fastapi_app_import', exc)
        checks.append(False)

    out_path = ROOT / 'outputs/review_result.json'
    if out_path.exists():
        data = json.loads(out_path.read_text(encoding='utf-8'))
        required = ['request_id', 'status', 'original_text', 'revised_text', 'retrieval_results', 'llm_review_result', 'diff_ops']
        miss = [k for k in required if k not in data]
        if miss:
            print('[FAIL] output_fields_missing', miss)
            checks.append(False)
        else:
            print('[PASS] output_fields')
            checks.append(True)
    else:
        print('[FAIL] output_missing')
        checks.append(False)

    try:
        from src.api.schemas.errors import ErrorCode
        expected = {'INVALID_INPUT','PIPELINE_FAILED','RETRIEVER_NOT_FOUND','RETRIEVAL_FAILED','RULE_CHECK_FAILED','LLM_DISABLED','LLM_CALL_FAILED','LLM_SCHEMA_INVALID','DIFF_FAILED','OUTPUT_SCHEMA_INVALID','UNKNOWN_ERROR'}
        got = {e.value for e in ErrorCode}
        if expected.issubset(got):
            print('[PASS] error_codes')
            checks.append(True)
        else:
            print('[FAIL] error_codes')
            checks.append(False)
    except Exception as exc:  # noqa: BLE001
        print('[FAIL] error_codes_import', exc)
        checks.append(False)

    if all(checks):
        print('All regression checks passed.')
        return 0
    print('Regression checks failed.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
