import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_us_momentum(stock_list):
    """
    미국 주가/거래량 모멘텀 계산 (yfinance 기반)
    """
    # 날짜 범위 설정
    ED = datetime.today() # 오늘
    SD = ED - timedelta(days=500) # 주간/월간/연간 모멘텀을 위해 넉넉히 500일 전 데이터 요청
    
    # yfinance로 한 번에 여러 종목을 수집하면 빠름 (단기/중기/장기 모두를 위해 Daily 데이터 사용)
    # yfinance 호환을 위해 티커의 / 을 - 로 변경 (예: BRK/B -> BRK-B)
    stock_list = {k.replace('/', '-'): v for k, v in stock_list.items()}
    tickers = list(stock_list.keys())
    
    # 1. 주가 및 거래량 데이터 일괄 수집 (yfinance.download)
    # yfinance는 한 번에 여러 티커를 넣으면 컬럼이 MultiIndex가 됨
    data = yf.download(tickers, start=SD, end=ED, interval='1d' ,progress=False)

    def get_each_momentum(ticker):
        try:
            # 해당 종목의 데이터 추출 (종가, 거래량)
            df = data[['Close', 'Volume']].xs(ticker, axis=1, level=1)
            df = df.dropna()
            
            if len(df) < 20: 
                return None, None
                
            # 2. 주가 모멘텀 지표 생성
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
                mom_1y = ( df.iloc[-1]['Close'] / df.iloc[-250]['Close'] - 1 )  * 100
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
            
        except:
            return None, None

    # 모멘텀 지표 계산 후 result에 적재
    result = []
    print(f"미국 모멘텀 분석 시작... (대상 건수: {len(tickers)})")
    
    for ticker in tickers:
        avg, vol = get_each_momentum(ticker)
        sname = stock_list.get(ticker, ticker)
        result.append([ticker, sname, avg, vol])
    
    # 모멘텀 지표 결과(result)는 데이터프레임(data_mom)으로 저장
    data_mom = pd.DataFrame(result, columns=['scode', 'sname', 'mom_price', 'mom_vol'])
    
    # 추출 오류 종목 제외
    data_mom = data_mom.dropna().reset_index(drop=True)
    
    return data_mom
