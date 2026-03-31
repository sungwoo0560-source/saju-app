import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')
from saju_engine import SajuCoreEngine
import inspect
print(inspect.signature(SajuCoreEngine.__init__))
# 실제 사용 방식 찾기
src = inspect.getsource(SajuCoreEngine)
print(src[:500])
