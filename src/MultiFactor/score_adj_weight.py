import pandas as pd
import numpy as np

def get_score_adj_weight(data_mast, weight='균등'):

    def score_regenerate(data_mast, cols, df_w):
        # 가중치 적용을 위한 멀티팩터 마스터(data_mast)의 복사본(dat_weight) 생성  
        data_weight = data_mast.copy() 
        
        # 가중치를 적용하여 종합점수 생성 
        data_weight['종합점수'] = np.average( data_weight[cols], axis=1, weights=df_w['weights']) 
        
        # 종합순위 및 종합순위 퍼센트 생성 
        data_weight['종합순위'] = data_weight['종합점수'].rank(ascending=True, axis=0)
        data_weight['종합순위_퍼센트'] = data_weight['종합순위'] / len(data_weight) * 100
        
        # 종합순위 순으로 정렬
        data_weight.sort_values(by='종합순위', inplace=True)

        return data_weight 

        
    
    # 가중치 벡터 초기화 
    cols = ['모멘텀_주가', '모멘텀_거래량', '밸류_PER', '밸류_PBR', '퀄리티_ROE', '퀄리티_매출증가', '퀄리티_영업이익증가', '퀄리티_순이익증가']
    df_w = pd.DataFrame()
    df_w['cols'] = cols
    

    # ① 가치 성장 전략 (밸류 + 퀄리티 조합)
    if weight == '가치성장':        
        df_w['weights'] = [0/8, 0/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8]
        data_mast = score_regenerate(data_mast, cols, df_w) 
        return data_mast

    # ② 추세 성장 전략 (모멘텀 + 퀄리티 조합)
    elif weight == '추세성장':        
        df_w['weights'] = [1/8, 1/8, 0/8, 0/8, 1/8, 1/8, 1/8, 1/8]    
        data_mast = score_regenerate(data_mast, cols, df_w) 
        return data_mast
    
    # ③ 역발상 전략 (밸류 + 모멘텀 조합)
    elif weight == '역발상':        
        df_w['weights'] = [1/8, 1/8, 1/8, 1/8, 0/8, 0/8, 0/8, 0/8]  
        data_mast = score_regenerate(data_mast, cols, df_w) 
        return data_mast

    # ③ 균등
    elif weight == '균등':        
        df_w['weights'] = [1/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8]  
        data_mast = score_regenerate(data_mast, cols, df_w) 
        return data_mast

    else:
        print("(옵션입력 오류) 다음 옵션 중에 하나를 입력하세요. : 가치성장,추세성장,역발상,균등")
        return None

