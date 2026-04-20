import FinanceDataReader as fdr

import pandas as pd
import numpy as np

def get_us_stockinfo(N=500): 
    """
    미국 종목정보 추출 (GitHub 시가총액 데이터 + FDR 상세정보 병합)
    """
    url = "https://raw.githubusercontent.com/Ate329/top-us-stock-tickers/master/tickers/sp500.csv"
    
    try:
        # 1. GitHub에서 최신 S&P 500 데이터 로드 (시가총액 등 순위용)
        df = pd.read_csv(url)
        
        # 2. FDR에서 KR/US 전체 상장 종목 정보 로드 (명칭 일관성 유지)
        df_sp500 = fdr.StockListing('S&P500')
        df_nasdaq = fdr.StockListing('NASDAQ')
        df_nyse = fdr.StockListing('NYSE')
        
        # 3. FDR 데이터 병합 및 중복 제거
        fdr_stocks = pd.concat([df_sp500, df_nasdaq, df_nyse])
        fdr_stocks = fdr_stocks.drop_duplicates(subset='Symbol')
        
        # 4. Symbol 기준으로 조인하여 FDR의 Name을 사용
        # fdr_stocks 에는 Symbol, Name, Sector, Industry 컬럼이 포함됨
        df = df.merge(fdr_stocks[['Symbol', 'Name']], left_on='symbol', right_on='Symbol', how='left')
        
        # 5. 컬럼명을 기존 시스템과 동일하게 변경 (GitHub의 name 대신 FDR의 Name 사용)
        column_map = {
            'symbol': 'Code',
            'Name': 'Name',
            'marketCap': 'MarketCap',
            'industry': 'Industry',
            'price': 'Price',
            'volume': 'Volume'
        }
        df = df.rename(columns=column_map)
        
        # 6. 시가총액 순으로 내림차순 정렬
        if 'MarketCap' in df.columns:
            df = df.sort_values(by='MarketCap', ascending=False)
            
    except Exception as e:
        print(f"데이터 로드 및 상세 정보 병합 실패: {e}. 기본 FDR 방식으로 전환합니다.")
        try:
            df_sp500 = fdr.StockListing('S&P500')
            df_nasdaq = fdr.StockListing('NASDAQ')
            df_nyse = fdr.StockListing('NYSE')
            df = pd.concat([df_sp500, df_nasdaq, df_nyse]).drop_duplicates(subset='Symbol')
        except:
            df_nasdaq = fdr.StockListing('NASDAQ')
            df_nyse = fdr.StockListing('NYSE')
            df = pd.concat([df_nasdaq, df_nyse]).drop_duplicates(subset='Symbol')
        
        if 'Symbol' in df.columns:
            df = df.rename(columns={'Symbol': 'Code'})

    # 7. 종목코드 클렌징 (yfinance 호환을 위해 / 를 - 로 변경. 예: BRK/B -> BRK-B)
    if 'Code' in df.columns:
        df['Code'] = df['Code'].str.replace('/', '-', regex=False)

    # 8. 상위 N개 추출 및 인덱스 초기화
    df = df.head(N).reset_index(drop=True)
    
    # 9. 요청된 필수 컬럼만 필터링 (Code, Name, Price, MarketCap, Volume, Industry)
    target_cols = ['Code', 'Name', 'Price', 'MarketCap', 'Volume', 'Industry']
    # 존재하는 컬럼만 선택 (fallback 시 일부 컬럼이 없을 수 있음 대비)
    available_cols = [col for col in target_cols if col in df.columns]
    df = df[available_cols]
    
    print("미국 종목 추출 건수 ", len(df))
    
    return df
