import FinanceDataReader as fdr

import pandas as pd
import numpy as np

def get_us_stockinfo(N=500): 
    """
    미국 종목정보 추출 (S&P 500 기준 또는 전체 거래소)
    """
    # S&P 500 종목 리스트 가져오기 (가장 안정적인 대형주 500개)
    # 만약 전체 거래소 상위 500개를 원한다면 별도 로직 필요하나 S&P 500이 '시가총액 500개'에 가장 부합하는 기본 리스트임
    try:
        df = fdr.StockListing('S&P500')
    except:
        # S&P500 리스트 실패 시 NASDAQ, NYSE 등에서 시가총액 상위 추출 시도
        df_nasdaq = fdr.StockListing('NASDAQ')
        df_nyse = fdr.StockListing('NYSE')
        df = pd.concat([df_nasdaq, df_nyse])

    # 종목 추출 건수 체크 및 필터링 (필요 시)
    # 미국 주식은 이미 fdr 리스트에 시가총액 정보 등이 포함되어 있을 수 있음
    # 하지만 yfinance 호환을 위해 'Symbol' 또는 'Ticker' 컬럼이 중요함
    
    if 'Symbol' in df.columns:
        df = df.rename(columns={'Symbol': 'Code'})
    
    # 상위 N개 추출
    df = df.head(N)
    
    # 데이터프레임 인덱스 초기화
    df = df.reset_index(drop=True)
    
    print("미국 종목 추출 건수 ", len(df))
    
    return df
