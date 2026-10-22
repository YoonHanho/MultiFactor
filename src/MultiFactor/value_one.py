import FinanceDataReader as fdr

import pandas as pd
import numpy as np

try:
    from .daum_consensus import get_daum_finstate
except ImportError:
    from daum_consensus import get_daum_finstate


def get_value_one(scode):
    
    result = []
    
    try:
        # 1. SnapDataReader 먼저 시도 -> 에러 시 다음증권 컨센서스로 대체
        try:
            data = fdr.SnapDataReader(f'NAVER/FINSTATE-2Y/{scode}').dropna(subset='영업이익') # 연간
        except Exception:
            data = get_daum_finstate(scode, freq='Y').dropna(subset='영업이익')

        per_series = data['PER(배)'].dropna()
        pbr_series = data['PBR(배)'].dropna()
        per = per_series.iloc[-1] if not per_series.empty else np.nan
        pbr = pbr_series.iloc[-1] if not pbr_series.empty else np.nan
        result.append([scode, per, pbr])
        data_val = pd.DataFrame(result, columns=['scode', 'PER', 'PBR'])
        return data_val 

    except Exception as e:
        print(f"에러가 발생했습니다. 상세 내용: {e}")
        print("추출오류 : ", scode) # 에러 종목코드 출력
        return None   
