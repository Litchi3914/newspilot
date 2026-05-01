import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import argparse, json
from src.diff.text_diff import TextDiffGenerator

def main():
    p=argparse.ArgumentParser(); p.add_argument('--original',default='examples/sample_draft.txt'); p.add_argument('--revised',default='outputs/revised_text.txt')
    a=p.parse_args(); o=Path(a.original).read_text(encoding='utf-8'); rv=Path(a.revised).read_text(encoding='utf-8') if Path(a.revised).exists() else o+'\n【待补充】'
    diff=TextDiffGenerator().generate(o,rv)
    Path('outputs/diff_result.json').write_text(json.dumps({'diff_ops':diff},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__': main()
