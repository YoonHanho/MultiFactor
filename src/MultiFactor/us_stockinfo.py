import FinanceDataReader as fdr

import pandas as pd
import numpy as np

def get_us_stockinfo(N=500): 
    """
    미국 종목정보 추출 (GitHub S&P 500 데이터 활용 및 정렬)
    """
    url = "https://raw.githubusercontent.com/Ate329/top-us-stock-tickers/master/tickers/sp500.csv"
    
    try:
        # 1. GitHub에서 최신 S&P 500 데이터 로드
        df = pd.read_csv(url)
        
        # 2. 컬럼명을 기존 시스템과 동일하게 변경
        column_map = {
            'symbol': 'Code',
            'name': 'Name',
            'marketCap': 'MarketCap',
            'industry': 'Industry',
            'price': 'Price',
            'volume': 'Volume'
        }
        df = df.rename(columns=column_map)
        
        # 3. 시가총액 순으로 내림차순 정렬
        if 'MarketCap' in df.columns:
            df = df.sort_values(by='MarketCap', ascending=False)
            
    except Exception as e:
        print(f"GitHub 데이터 로드 실패: {e}. 기존 FDR 방식으로 전환합니다.")
        # 실패 시 기존 FinanceDataReader 로직 사용
        try:
            df = fdr.StockListing('S&P500')
        except:
            df_nasdaq = fdr.StockListing('NASDAQ')
            df_nyse = fdr.StockListing('NYSE')
            df = pd.concat([df_nasdaq, df_nyse])
        
        if 'Symbol' in df.columns:
            df = df.rename(columns={'Symbol': 'Code'})

    # 4. 상위 N개 추출 및 인덱스 초기화
    df = df.head(N).reset_index(drop=True)
    
    print("미국 종목 추출 건수 ", len(df))
    
    return df
