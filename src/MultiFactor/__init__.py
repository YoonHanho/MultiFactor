# src/MultiFactor/__init__.py
import warnings
import logging
import os

# 1. 모든 로그 비활성 (라이브러리 내부 chatter 차단)
logging.disable(logging.CRITICAL)
# 2. 모든 경고 무시
warnings.filterwarnings("ignore")
# 3. 환경 변수 수준에서 무시
os.environ['PYTHONWARNINGS'] = 'ignore'

# 같은 폴더의 core.py/us_core.py에서 클래스를 가져옵니다.
from .core import MultiFactorKR
from .us_core import MultiFactorUS

# 패키지를 import할 때 노출할 항목을 명시합니다.
__all__ = ['MultiFactorKR', 'MultiFactorUS']