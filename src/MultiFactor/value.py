import FinanceDataReader as fdr

import pandas as pd
import numpy as np

import time

def get_value(stock_list):
    
    result = []
    
    for i, (scode, sname) in enumerate(stock_list.items()):
    
        # [중요] 데이터 수집 시 서버 차단 방지 (1초 대기)
        time.sleep(1)
    
        # 진행 상황 모니터링 (50번째 순서마다 종목명 출력)
        if i % 50 == 0:
            print(f"{i}/{len(stock_list)} 진행 중... ({sname})")
    
        try:
            # 재무제표 데이터 추출 (연간 K-IFRS 연결 기준)
            data = fdr.SnapDataReader(f'NAVER/FINSTATE-2Y/{scode}').dropna(subset='영업이익') # 연간
            per, pbr = data['PER(배)'].iloc[-1], data['PBR(배)'].iloc[-1]
            result.append([scode, per, pbr])
    
        except:
            print("추출오류 : ", sname) # 에러 종목코드 출력
            result.append([scode, None, None])

    
    data_val = pd.DataFrame(result, columns=['scode', 'PER', 'PBR'])

    return data_val 