"""
conftest.py — pytest 루트 설정.

스킬 루트를 sys.path에 추가해 모든 tests/ 파일이
`from evaluator.run import ...` 형태로 import 가능하게 한다.
"""
import sys
from pathlib import Path

# 이 파일(conftest.py)이 있는 디렉터리 = 스킬 루트
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
