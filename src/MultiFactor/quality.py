import FinanceDataReader as fdr

import pandas as pd
import numpy as np

import time

try:
    from .daum_consensus import get_daum_finstate
except ImportError:
    from daum_consensus import get_daum_finstate


def get_quality(stock_list):
    result_fin = []
    for i, (scode, sname) in enumerate(stock_list.items()):
    
        # [중요] 1. 서버 차단 방지 (1초 대기)
        time.sleep(1)
    
        # 진행 상황 모니터링 (50개마다 출력)
        if i % 50 == 0:
            print(f"{i}/{len(stock_list)} 진행 중... ({sname})")
    
        try:
            # 재무 데이터 추출 : 1. SnapDataReader 먼저 시도 -> 에러 시 다음증권 컨센서스로 대체
            try:
                data = fdr.SnapDataReader(f'NAVER/FINSTATE-2Q/{scode}').dropna(subset='영업이익')  # 분기
            except Exception:
                data = get_daum_finstate(scode, freq='Q').dropna(subset='영업이익')

            fin = (data[['매출액','영업이익','당기순이익']].pct_change()*100).iloc[-1].to_list()
            roe_series = data['ROE(%)'].dropna()
            roe = roe_series.iloc[-1] if not roe_series.empty else np.nan
            result_fin.append([scode] + fin + [roe])
    
        except:
            print("추출오류 : ", sname) # 에러 종목코드 출력
            result_fin.append([scode, None, None, None, None])
    
    
    # ROE와 나머지 지표를 결합하여, 퀄러티 지표 완성
    data_fin = pd.DataFrame(result_fin, columns=['scode', 'revenue_rate', 'oper_income_rate', 'net_income_rate', 'ROE'])

    return data_fin
