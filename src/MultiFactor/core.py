#!pip install finance-datareader

import FinanceDataReader as fdr

import pandas as pd
import numpy as np

import time 

from . import stockinfo as sinfo

from . import momentum as mom 
from . import value as val 
from . import quality as qual

from . import momentum_one as mom1 
from . import value_one as val1
from . import quality_one as qual1

from . import score as sc
from . import score_adj_weight as scw



class MultiFactorKR:
    def __init__(self, N: int):
        """
        멀티팩터 : 분석 대상 종목수 (시가총액 상위 N개)
        """    
        self.N = N
		

    def get_stockinfo(self, dtype='dataframe') -> pd.DataFrame:
        
        df = sinfo.get_stockinfo(self.N)
        
        if dtype=='dic':
        # 종목 정보 사전 저장
            stock_list = dict(zip(df['Code'], df['Name']))    
            return stock_list

        else:
            return df


    
    def get_momentum(self, stock_list) -> pd.DataFrame:
        """
        모멘텀 
        """
        data_mom = mom.get_momentum(stock_list) 
        return data_mom 
        

    def get_momentum_one(self, scode) -> pd.DataFrame:
        """
        모멘텀 1개 종목 
        """
        return mom1.get_momentum_one(scode)

    def get_value(self, stock_list) -> pd.DataFrame:
        """
        밸류
        """
        data_val = val.get_value(stock_list) 
        return data_val 
        
    def get_value_one(self, scode) -> pd.DataFrame:
        """
        밸류 1개 종목 
        """ 
        return val1.get_value_one(scode)

    def get_quality(self, stock_list) -> pd.DataFrame:
        """
        퀄리티 
        """
        data_fin = qual.get_quality(stock_list) 
        return data_fin

    def get_quality_one(self, scode) -> pd.DataFrame:
        """
        퀄리티 1개 종목 
        """
        return qual1.get_quality_one(scode)



    def get_score(self) -> pd.DataFrame:
        """
        스코어 마스터 자동계산 
        """
        print("(1/5) 종목코드 생성")
        stock_list = self.get_stockinfo(dtype='dic')
        
        print("\n(2/5) 모멘텀 지표 생성")
        data_mom = self.get_momentum(stock_list)
        
        print("\n(3/5) 밸류 지표 생성")
        data_val = self.get_value(stock_list)
        
        print("\n(4/5) 퀄리티 지표 생성")
        data_fin = self.get_quality(stock_list)
        
        print("\n(5/5) 멀티팩터 마스터 생성")        
        data_mast = sc.get_score(data_mom, data_val, data_fin)
        
        data_mast.reset_index(drop=True, inplace=True) 
        
        return data_mast 

    
    def get_score_by_data(self, data_mom, data_val, data_fin) -> pd.DataFrame:
        """
        스코어 마스터 : 직접 데이터 입력 
        """
        data_mast = sc.get_score(data_mom, data_val, data_fin)
        data_mast.reset_index(drop=True, inplace=True) 
        return data_mast 

        
    def get_score_adj_weight(self, data_mast, weight='균등') -> pd.DataFrame:
        """
        스코어 마스터를 받아서, 가중치 주기 
        weight : 균등(기본), 가치성장, 추세성장, 역발생 
        """
        data_mast = scw.get_score_adj_weight(data_mast, weight)
        data_mast.reset_index(drop=True, inplace=True) 
        return data_mast 


    def get_Ngroup(self, data_mast, Ngroup=10) -> pd.DataFrame:
        """
        지정한 그룹수(Ngroup)에 따라 종목명만 출력 
        Ngroup : 2부터 100 사이값 & data_mast보다 건수 적음
        """
        Ngroup = int(Ngroup)
        if Ngroup > 1 and Ngroup <= 100 and Ngroup < len(data_mast):

            # 1. 종합순위를 기준으로 오름차순 정렬
            data_mast = data_mast.sort_values(by='종합순위')
            
            # 2. 정렬된 데이터프레임을 Ngroup 개수만큼 분할
            chunks = np.array_split(data_mast, Ngroup)
        
             # 3. 각 그룹별로 번호와 종목명 출력
            for i, chunk in enumerate(chunks, 1):
                stock_list = ", ".join(chunk['sname'].astype(str).tolist())
                print(f"{i} : {stock_list}")
        
        else: 
            print("Ngroup를 다시 입력하세요 : 2부터 100 사이값으로, 멀티팩터 데이터보다 건수가 적어야 합니다") 
        

        

    

        


        

        


        

