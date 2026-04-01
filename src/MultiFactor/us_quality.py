import yfinance as yf
import pandas as pd
import numpy as np
import time

def get_us_quality(stock_list):
    """
    미국 주식 퀄리티 계산 (yfinance 기반)
    revenue_rate, oper_income_rate, net_income_rate, ROE 등 
    """
    result_fin = []
    
    for i, (scode, sname) in enumerate(stock_list.items()):
        
        # 서버 차단 방지 (yfinance 요청 제한 고려)
        time.sleep(0.1)
        
        # 진행 상황 모니터링 (50개마다 출력)
        if i % 50 == 0:
            print(f"퀄리티 분석 {i}/{len(stock_list)} 진행 중... ({sname})")
    
        try:
            ticker = yf.Ticker(scode)
            info = ticker.info
            
            # yfinance info에서 성장을 확인하거나, financials(분기) 데이터를 직접 가공
            # info.revenueGrowth, earningsGrowth 등이 있으면 사용, 없으면 Na 처리
            revenue_rate = info.get('revenueGrowth', np.nan) * 100 # yfinance는 소수점 단위가 많아 100을 곱함
            oper_income_rate = info.get('operatingMargins', np.nan) # 미국은 마진 정보가 많음 
            net_income_rate = info.get('earningsGrowth', np.nan) * 100
            roe = info.get('returnOnEquity', np.nan) * 100 if info.get('returnOnEquity') else np.nan
            
            result_fin.append([scode, revenue_rate, oper_income_rate, net_income_rate, roe])
    
        except:
            print("추출오류 (퀄리티) : ", scode) # 에러 종목코드 출력
            result_fin.append([scode, None, None, None, None])
    
    # 컬럼 구조는 기존 한국 서비스와 동일하게 맞춤(revenue_rate, oper_income_rate, net_income_rate, ROE)
    data_fin = pd.DataFrame(result_fin, columns=['scode', 'revenue_rate', 'oper_income_rate', 'net_income_rate', 'ROE'])

    return data_fin
