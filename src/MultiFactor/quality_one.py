import FinanceDataReader as fdr

import pandas as pd
import numpy as np

try:
    from .daum_consensus import get_daum_finstate
except ImportError:
    from daum_consensus import get_daum_finstate


def get_quality_one(scode):
    result_fin = []
    try:
        # 1. SnapDataReader 먼저 시도 -> 에러 시 다음증권 컨센서스로 대체
        try:
            data = fdr.SnapDataReader(f'NAVER/FINSTATE-2Q/{scode}').dropna(subset='영업이익')  # 분기
        except Exception:
            data = get_daum_finstate(scode, freq='Q').dropna(subset='영업이익')

        fin = (data[['매출액','영업이익','당기순이익']].pct_change()*100).iloc[-1].to_list()
        roe_series = data['ROE(%)'].dropna()
        roe = roe_series.iloc[-1] if not roe_series.empty else np.nan
        result_fin.append([scode] + fin + [roe])
        data_fin = pd.DataFrame(result_fin, columns=['scode', 'revenue_rate', 'oper_income_rate', 'net_income_rate', 'ROE'])
        return data_fin

    except Exception as e:
        print(f"에러가 발생했습니다. 상세 내용: {e}")
        print("추출오류 : ", scode) # 에러 종목코드 출력
        return None 