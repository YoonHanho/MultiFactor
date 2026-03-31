import FinanceDataReader as fdr

import pandas as pd
import numpy as np


def get_quality_one(scode):
    result_fin = []
    try:
        # 재무 데이터 추출 : 분기 K-IFRS 연결 기준
        data = fdr.SnapDataReader(f'NAVER/FINSTATE-2Q/{scode}').dropna(subset='영업이익')  # 분기
        fin = (data[['매출액','영업이익','당기순이익']].pct_change()*100).iloc[-1].to_list()
        roe = data['ROE(%)'].iloc[-1]
        result_fin.append([scode] + fin + [roe])
        data_fin = pd.DataFrame(result_fin, columns=['scode', 'revenue_rate', 'oper_income_rate', 'net_income_rate', 'ROE'])
        return data_fin

    except Exception as e:
        print(f"에러가 발생했습니다. 상세 내용: {e}")
        print("추출오류 : ", sname) # 에러 종목코드 출력
        return None 