import FinanceDataReader as fdr

import pandas as pd
import numpy as np

import time

try:
    from .daum_consensus import get_daum_finstate
except ImportError:
    from daum_consensus import get_daum_finstate

def get_value(stock_list):
    
    result = []
    
    for i, (scode, sname) in enumerate(stock_list.items()):
    
        # [중요] 데이터 수집 시 서버 차단 방지 (1초 대기)
        time.sleep(1)
    
        # 진행 상황 모니터링 (50번째 순서마다 종목명 출력)
        if i % 50 == 0:
            print(f"{i}/{len(stock_list)} 진행 중... ({sname})")
    
        try:
            # 재무제표 데이터 추출 : 1. SnapDataReader 먼저 시도 -> 에러 시 다음증권 컨센서스로 대체
            try:
                data = fdr.SnapDataReader(f'NAVER/FINSTATE-2Y/{scode}').dropna(subset='영업이익') # 연간
            except Exception:
                data = get_daum_finstate(scode, freq='Y').dropna(subset='영업이익')

            per_series = data['PER(배)'].dropna()
            pbr_series = data['PBR(배)'].dropna()
            per = per_series.iloc[-1] if not per_series.empty else np.nan
            pbr = pbr_series.iloc[-1] if not pbr_series.empty else np.nan
            result.append([scode, per, pbr])
    
        except Exception as e:
            print("추출오류 : ", sname, f"({type(e).__name__}: {e})") # 에러 종목코드 및 원인 출력
            result.append([scode, None, None])

    
    data_val = pd.DataFrame(result, columns=['scode', 'PER', 'PBR'])

    return data_val 