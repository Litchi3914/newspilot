import json
import os
from datetime import datetime
from pathlib import Path


def _check_import(module_name: str) -> tuple[bool, str]:
    try:
        __import__(module_name)
        return True, 'ok'
    except Exception as exc:  # noqa: BLE001
        return False, f'{type(exc).__name__}: {exc}'


def _probe_openai_sdk_chat(base_url: str, api_key: str, model: str, timeout: int = 20) -> tuple[bool, str]:
    if not base_url:
        return False, 'base_url is empty'
    if not api_key:
        return False, 'api_key is empty'
    if not model:
        return False, 'model is empty'

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key, base_url=base_url)
        resp = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': 'reply with ok only'}],
            temperature=0,
            timeout=timeout,
        )
        content = ''
        if resp and resp.choices:
            content = (resp.choices[0].message.content or '').strip()
        if content:
            return True, f'sdk_chat_ok: {content[:60]}'
        return True, 'sdk_chat_ok: empty-content'
    except Exception as exc:  # noqa: BLE001
        return False, f'{type(exc).__name__}: {exc}'


def main() -> int:
    report = {
        'created_at': datetime.now().isoformat(timespec='seconds'),
        'llm': {},
        'embedding': {},
        'vectorstore': {},
        'python_deps': {},
        'summary': {},
    }

    llm_provider = os.getenv('LLM_PROVIDER', 'mock').lower()
    llm_model = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')
    llm_base_url = os.getenv('OPENAI_BASE_URL', '').strip()
    llm_enable = os.getenv('LLM_ENABLE_REAL_CALL', 'false').lower() in {'1', 'true', 'yes', 'on'}
    llm_api_key_env = os.getenv('LLM_API_KEY_ENV', 'OPENAI_API_KEY')
    llm_api_key = os.getenv(llm_api_key_env, '').strip()

    emb_provider = os.getenv('EMBEDDING_PROVIDER', 'none').lower()
    emb_model = os.getenv('EMBEDDING_MODEL', 'bge-m3')
    emb_base_url = os.getenv('EMBEDDING_BASE_URL', '').strip()

    vec_backend = os.getenv('VECTORSTORE_BACKEND', 'faiss').lower()

    report['llm'].update({
        'provider': llm_provider,
        'model': llm_model,
        'base_url': llm_base_url,
        'enable_real_call': llm_enable,
        'api_key_env': llm_api_key_env,
        'api_key_present': bool(llm_api_key),
    })

    if llm_provider == 'openai' and llm_enable:
        ok, msg = _probe_openai_sdk_chat(llm_base_url, llm_api_key, llm_model)
        report['llm']['endpoint_ok'] = ok
        report['llm']['endpoint_message'] = msg
    else:
        report['llm']['endpoint_ok'] = True
        report['llm']['endpoint_message'] = 'skipped (mock or disabled)'

    report['embedding'].update({
        'provider': emb_provider,
        'model': emb_model,
        'base_url': emb_base_url,
    })
    report['embedding']['endpoint_ok'] = True
    report['embedding']['endpoint_message'] = 'skipped (embedding sdk probe not enabled in preflight)'

    module_matrix = {
        'openai': 'openai',
        'pymilvus': 'pymilvus',
        'chromadb': 'chromadb',
        'faiss': 'faiss',
    }
    for key, module_name in module_matrix.items():
        ok, msg = _check_import(module_name)
        report['python_deps'][key] = {'installed': ok, 'message': msg}

    vec_ok = True
    vec_msg = 'ok'
    if vec_backend == 'milvus' and not report['python_deps']['pymilvus']['installed']:
        vec_ok = False
        vec_msg = 'missing pymilvus'
    elif vec_backend == 'chroma' and not report['python_deps']['chromadb']['installed']:
        vec_ok = False
        vec_msg = 'missing chromadb'
    elif vec_backend == 'faiss' and not report['python_deps']['faiss']['installed']:
        vec_ok = False
        vec_msg = 'missing faiss'

    report['vectorstore'].update({'backend': vec_backend, 'ready': vec_ok, 'message': vec_msg})

    hard_fail = []
    if llm_provider == 'openai' and llm_enable and not report['llm']['endpoint_ok']:
        hard_fail.append('LLM endpoint unavailable')
    if not vec_ok:
        hard_fail.append('Vector backend dependency missing')

    report['summary'] = {
        'ready': len(hard_fail) == 0,
        'hard_failures': hard_fail,
    }

    out_dir = Path('data/logs')
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / 'stack_preflight_report.json'
    md_path = out_dir / 'stack_preflight_report.md'

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = [
        '# Stack Preflight Report',
        '',
        f"- created_at: {report['created_at']}",
        f"- ready: {report['summary']['ready']}",
        '',
        '## LLM',
        f"- provider: {report['llm']['provider']}",
        f"- model: {report['llm']['model']}",
        f"- base_url: {report['llm']['base_url'] or '(empty)'}",
        f"- api_key_env: {report['llm']['api_key_env']}",
        f"- api_key_present: {report['llm']['api_key_present']}",
        f"- endpoint_ok: {report['llm']['endpoint_ok']}",
        f"- endpoint_message: {report['llm']['endpoint_message']}",
        '',
        '## Embedding',
        f"- provider: {report['embedding']['provider']}",
        f"- model: {report['embedding']['model']}",
        f"- base_url: {report['embedding']['base_url'] or '(empty)'}",
        f"- endpoint_ok: {report['embedding']['endpoint_ok']}",
        f"- endpoint_message: {report['embedding']['endpoint_message']}",
        '',
        '## Vectorstore',
        f"- backend: {report['vectorstore']['backend']}",
        f"- ready: {report['vectorstore']['ready']}",
        f"- message: {report['vectorstore']['message']}",
        '',
        '## Python Deps',
    ]
    for dep, detail in report['python_deps'].items():
        lines.append(f"- {dep}: installed={detail['installed']} ({detail['message']})")

    if report['summary']['hard_failures']:
        lines.extend(['', '## Hard Failures'])
        for x in report['summary']['hard_failures']:
            lines.append(f'- {x}')

    md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(f'Wrote: {json_path}')
    print(f'Wrote: {md_path}')
    if report['summary']['ready']:
        print('Preflight: PASS')
        return 0
    print('Preflight: FAIL')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
