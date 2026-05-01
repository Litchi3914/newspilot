import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts import _run07
if __name__=='__main__': _run07.main()
