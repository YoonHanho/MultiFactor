import pandas as pd
import numpy as np

def get_score(data_mom, data_val, data_fin):
    
    ## 종합지표 생성
    # 멀티팩터 마스터 파일 생성
    data_mast = data_mom.merge(data_val, on='scode', how='left')\
                        .merge(data_fin, on='scode', how='left')
    
    
    # 결측 보정
    # 멀티팩터 마스터파일에서 수치형 컬럼명을 추출하여 cols로 저장
    cols = data_mast.select_dtypes(exclude='object').columns
    
    # for문으로 cols에 저장된 컬럼명(멀티팩터)별로 반복. 결측치 발생시 중앙값으로 대체
    for col in cols:
        data_mast[col] = data_mast[col].replace([np.inf, -np.inf], np.nan) # 무한대 처리
        data_mast[col] = data_mast[col].fillna(data_mast[col].median())    # 결측치 처리
    
    # 종합점수 생성
    # 모멘텀 지표 순위화 : 값이 클수록 우수
    data_mast['모멘텀_주가'] = data_mast['mom_price'].rank(ascending=False, axis=0) / len(data_mast) * 100
    data_mast['모멘텀_거래량'] = data_mast['mom_vol'].rank(ascending=False, axis=0) / len(data_mast) * 100
    
    # 밸류 지표 순위화 : 값이 작을수록 우수
    data_mast['밸류_PER'] = data_mast['PER'].rank(ascending=True, axis=0) / len(data_mast) * 100
    data_mast['밸류_PBR'] = data_mast['PBR'].rank(ascending=True, axis=0) / len(data_mast) * 100
    data_mast['퀄리티_ROE'] = data_mast['ROE'].rank(ascending=False, axis=0) / len(data_mast) * 100
    
    # 퀄리티 지표 순위화 : 값이 클수록 우수
    data_mast['퀄리티_ROE'] = data_mast['ROE'].rank(ascending=False, axis=0) / len(data_mast) * 100
    data_mast['퀄리티_매출증가'] = data_mast['revenue_rate'].rank(ascending=False, axis=0) / len(data_mast) * 100
    data_mast['퀄리티_영업이익증가'] = data_mast['oper_income_rate'].rank(ascending=False, axis=0) / len(data_mast) * 100
    data_mast['퀄리티_순이익증가'] = data_mast['net_income_rate'].rank(ascending=False, axis=0) / len(data_mast) * 100
    
    # 멀티팩터 종합점수 계산 컬럼 정의
    cols = ['모멘텀_주가', '모멘텀_거래량', '밸류_PER', '밸류_PBR', '퀄리티_ROE', '퀄리티_매출증가', '퀄리티_영업이익증가', '퀄리티_순이익증가']
    
    # 종합점수 계산 (평균)
    data_mast['종합점수'] = np.average( data_mast[cols], axis=1 )
    
    # 종합순위 계산
    data_mast['종합순위'] = data_mast['종합점수'].rank(ascending=True, axis=0)
    
    # 종합순위 퍼센트 계산
    data_mast['종합순위_퍼센트'] = data_mast['종합순위'] / len(data_mast) * 100
    
    # 종합순위 상위 순으로 정렬
    data_mast.sort_values(by='종합순위', inplace=True)
    
    # 화면에 종합순위 상위 10개 종목 출력 (T옵션으로 행과 열을 교환하여 출력)
    #data_mast.head(10).T

    return data_mast