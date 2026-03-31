import FinanceDataReader as fdr

import pandas as pd
import numpy as np

from datetime import date

def get_momentum(stock_list):

    # 날짜 : SD 작년 1/2, ED는 오늘 
    ED = date.today().strftime('%Y%m%d')   # 오늘
    
    last_year = date.today().year - 1
    SD = date(last_year, 1, 2).strftime('%Y%m%d')  # 작년 1월2일 


    def get_momentum_one(scode, SD, ED):
        """
        주가 모멘텀과 거래량 모멘텀 계산
    
        매개변수:
             scode : 종목 코드 (예: '005930')
             SD : 주가데이터 추출시작일 (예: '20250102')
             ED : 주가데이터 추출종료일 (예: '20250131')
    
        반환값:
            avg : 주가 모멘텀 지표 (기간별 수익률 평균)
            vol : 거래량 모멘텀 지표
        """
    
        # 1. 주가 및 거래량 데이터 수집 (여기는 에러나면 멈춰서 확인해야 하므로 try-except 제거)
        df = fdr.DataReader(scode, SD, ED)
    
        # 2. 주가 모멘텀 지표 생성
        # 단기 (1일, 1주, 1개월) - 데이터가 너무 없으면 에러가 나는 게 맞으므로 그대로 둠
        mom_1d = ( df.iloc[-1]['Close'] / df.iloc[-2]['Close'] - 1 )  * 100    # 전일
        mom_1w = ( df.iloc[-1]['Close'] / df.iloc[-5]['Close'] - 1 )  * 100    # 주간
        mom_1m = ( df.iloc[-1]['Close'] / df.iloc[-20]['Close'] - 1 )  * 100   # 월간
    
        # 3개월간 (데이터 부족 시 NaN 처리)
        try:
            mom_3m = ( df.iloc[-1]['Close'] / df.iloc[-60]['Close'] - 1 )  * 100
        except:
            mom_3m = np.nan
    
        # 연간 (데이터 부족 시 NaN 처리)
        try:
            mom_1y = ( df.iloc[-1]['Close'] / df.iloc[-240]['Close'] - 1 )  * 100
        except:
            mom_1y = np.nan
    
        # 3. 기간별 수익률의 평균 계산 (NaN을 제외하고 평균 산출)
        avg = np.nanmean([mom_1d, mom_1w, mom_1m, mom_3m, mom_1y])
    
        # 4. 거래량 모멘텀 지표 생성
        try:
            vol_short = df['Volume'].rolling(window=5).mean().iloc[-1]  # 최근 5일
            vol_long = df['Volume'].rolling(window=20).mean().iloc[-1]  # 최근 20일
            vol = ( vol_short / vol_long - 1) * 100
        except:
            vol = np.nan
    
        return avg, vol

    
    # 모멘텀 지표 계산 후 result에 적재
    result = []
    for scode, sname in stock_list.items():
        try:
            mom, vol = get_momentum_one(scode, SD, ED)  # 주가 데이터 수집일(SD, ED)  ★★★
            result.append( [ scode, sname, mom, vol ] )
    
        except:
            print("추출오류 : ", sname) # 에러 종목코드 출력
            result.append([scode, sname, None, None])
    
    # 모멘텀 지표 결과(result)는 데이터프레임(data_mom)으로 저장
    data_mom = pd.DataFrame(result, columns=['scode', 'sname', 'mom_price', 'mom_vol'])
    
    # 추출 오류 종목 제외 (최근 상장 종목)
    data_mom = data_mom.dropna().reset_index(drop=True)
    
    return data_mom