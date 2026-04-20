import sys
import os
import warnings

# 시스템 환경 변수 및 파이썬 수준에서 모든 경고를 즉시 차단
os.environ['PYTHONWARNINGS'] = 'ignore'
warnings.simplefilter("ignore")

import pandas as pd
import numpy as np

# 현재 파일의 절대 경로를 기준으로 src 폴더 위치를 찾습니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

print(f"PYTHONPATH: {sys.path[0]}")

try:
    from MultiFactor import MultiFactorKR, MultiFactorUS
    print("MultiFactor 패키지 로드 성공")
except Exception as e:
    print(f"패키지 로드 에러: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def test_korea():
    print("\n" + "="*60)
    print("검증: 한국 주식 (시가총액 상위 10개)")
    print("="*60)
    
    mf_kr = MultiFactorKR(N=10)
    
    print("Step 1: 종목 리스트 생성 중...")
    stock_list = mf_kr.get_stockinfo(dtype='dic')
    print(f"대상 종목 수: {len(stock_list)}")
    
    print("\nStep 2: 전체 분석 및 스코어 계산 중...")
    # get_score 내부에서 ZeroDivisionError가 발생하는지 확인
    try:
        data_mast = mf_kr.get_score()
        if data_mast is None or len(data_mast) == 0:
            print("[경고] 분석 데이터가 없습니다.")
            return

        print("\n[한국 주식 결과 (상위 10개)]")
        cols = ['scode', 'sname', '종합순위', '종합점수']
        actual_cols = [c for c in cols if c in data_mast.columns]
        print(data_mast.head(10)[actual_cols].reset_index(drop=True))
    except Exception as e:
        print(f"\n[오류] 한국 주식 분석 중 예외 발생: {e}")
        import traceback
        traceback.print_exc()

def test_us():
    print("\n" + "="*60)
    print("검증: 미국 주식 (시가총액 상위 10개)")
    print("="*60)
    
    mf_us = MultiFactorUS(N=500)
    
    print("Step 1: 미국 종목 리스트 생성 중...")
    stock_list = mf_us.get_stockinfo(dtype='dic')
    print(f"대상 미국 종목 수: {len(stock_list)}")
    
    print("\nStep 2: yfinance 기반 분석 및 스코어 계산 중...")
    try:
        data_mast = mf_us.get_score()
        if data_mast is None or len(data_mast) == 0:
            print("[경고] 미국 주식 분석 데이터가 없습니다.")
            return

        print("\n[미국 주식 결과 (상위 10개)]")
        # 미국주는 sname이 ticker일 수도 있음
        name_col = 'sname' if 'sname' in data_mast.columns else 'scode'
        cols = [name_col, '종합순위', '종합점수']
        actual_cols = [c for c in cols if c in data_mast.columns]
        print(data_mast.head(10)[actual_cols].reset_index(drop=True))
    except Exception as e:
        print(f"\n[오류] 미국 주식 분석 중 예외 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # test_korea()
    test_us()
    print("\n모든 검증 프로세스가 끝났습니다.")
