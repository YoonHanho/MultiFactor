import pandas as pd
import numpy as np

# 미국 전용 모듈 임포트 (새로 생성한 파일들)
from . import us_stockinfo as sinfo_us
from . import us_momentum as mom_us
from . import us_value as val_us
from . import us_quality as qual_us

# 공용 모듈 (기존 모듈 재사용)
from . import score as sc
from . import score_adj_weight as scw

class MultiFactorUS:
    def __init__(self, N: int = 500):
        """
        미국 주식 멀티팩터 : 분석 대상 종목수 (시가총액 상위 N개)
        """    
        self.N = N
		

    def get_stockinfo(self, dtype='dataframe') -> pd.DataFrame:
        """
        시가총액 상위 N개 종목 추출 
        """
        df = sinfo_us.get_us_stockinfo(self.N)
        
        if dtype=='dic':
            # 종목 정보 사전 저장 (Code, Name 구조 유지)
            # 미국주의 경우 Name 대신 Name 혹은 Ticker 그 자체 사용 가능
            name_col = 'Name' if 'Name' in df.columns else 'Code'
            stock_list = dict(zip(df['Code'], df[name_col]))    
            return stock_list
        else:
            return df


    def get_momentum(self, stock_list) -> pd.DataFrame:
        """
        미국 모멘텀 분석
        """
        data_mom = mom_us.get_us_momentum(stock_list) 
        return data_mom 
        

    def get_value(self, stock_list) -> pd.DataFrame:
        """
        미국 밸류 분석
        """
        data_val = val_us.get_us_value(stock_list) 
        return data_val 
        

    def get_quality(self, stock_list) -> pd.DataFrame:
        """
        미국 퀄리티 분석 
        """
        data_fin = qual_us.get_us_quality(stock_list) 
        return data_fin


    def get_score(self) -> pd.DataFrame:
        """
        미국 스코어 마스터 자동계산 (기존 score.py 로직 활용)
        """
        print("(1/5) 미국 종목코드 생성")
        stock_list = self.get_stockinfo(dtype='dic')
        
        print("\n(2/5) 미국 모멘텀 지표 생성")
        data_mom = self.get_momentum(stock_list)
        
        print("\n(3/5) 미국 밸류 지표 생성")
        data_val = self.get_value(stock_list)
        
        print("\n(4/5) 미국 퀄리티 지표 생성")
        data_fin = self.get_quality(stock_list)
        
        print("\n(5/5) 미국 멀티팩터 마스터 생성")        
        # 기존 한국 score.py의 get_score 함수를 그대로 활용 
        data_mast = sc.get_score(data_mom, data_val, data_fin)
        
        data_mast.reset_index(drop=True, inplace=True) 
        
        return data_mast 


    def get_score_adj_weight(self, data_mast, weight='균등') -> pd.DataFrame:
        """
        가중치 조정 (기존 score_adj_weight.py 로직 활용)
        """
        data_mast = scw.get_score_adj_weight(data_mast, weight)
        data_mast.reset_index(drop=True, inplace=True) 
        return data_mast 


    def get_Ngroup(self, data_mast, Ngroup=10) -> pd.DataFrame:
        """
        그룹별 출력 
        """
        Ngroup = int(Ngroup)
        if Ngroup > 1 and Ngroup <= 100 and Ngroup < len(data_mast):
            data_mast = data_mast.sort_values(by='종합순위')
            chunks = np.array_split(data_mast, Ngroup)
            for i, chunk in enumerate(chunks, 1):
                stock_list = ", ".join(chunk['sname'].astype(str).tolist())
                print(f"{i} : {stock_list}")
        else: 
            print("Ngroup를 다시 입력하세요") 
