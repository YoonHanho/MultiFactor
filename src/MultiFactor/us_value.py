import yfinance as yf
import pandas as pd
import numpy as np
import time

def get_us_value(stock_list):
    """
    미국 주식 밸류 계산 (yfinance 기반)
    참고: yfinance의 Ticker.info를 사용하므로 다수 종목 수집 시 시간이 소요됩니다.
    """
    result = []
    
    for i, (scode, sname) in enumerate(stock_list.items()):
        
        # 서버 차단 방지를 위한 짧은 휴식 (500개이므로 상황에 따라 조정 필요)
        # yfinance는 과도한 요청 시 차단될 수 있으므로 약간의 간격 권장
        time.sleep(0.1) 
        
        # 진행 상황 모니터링
        if i % 50 == 0:
            print(f"밸류 분석 {i}/{len(stock_list)} 진행 중... ({sname})")
    
        try:
            ticker = yf.Ticker(scode)
            info = ticker.info
            
            # yfinance는 trailingPE, priceToBook 등을 사용 
            per = info.get('trailingPE')
            pbr = info.get('priceToBook')
            
            result.append([scode, per, pbr])
    
        except:
            print("추출오류 (밸류) : ", scode) # 에러 종목코드 출력
            result.append([scode, None, None])

    data_val = pd.DataFrame(result, columns=['scode', 'PER', 'PBR'])

    return data_val 
