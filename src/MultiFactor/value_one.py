import FinanceDataReader as fdr

import pandas as pd
import numpy as np


def get_value_one(scode):
    
    result = []
    
    try:
        # 재무제표 데이터 추출 (연간 K-IFRS 연결 기준)
        data = fdr.SnapDataReader(f'NAVER/FINSTATE-2Y/{scode}').dropna(subset='영업이익') # 연간
        per, pbr = data['PER(배)'].iloc[-1], data['PBR(배)'].iloc[-1]
        result.append([scode, per, pbr])
        data_val = pd.DataFrame(result, columns=['scode', 'PER', 'PBR'])
        return data_val 

    except Exception as e:
        print(f"에러가 발생했습니다. 상세 내용: {e}")
        print("추출오류 : ", sname) # 에러 종목코드 출력
        return None   
