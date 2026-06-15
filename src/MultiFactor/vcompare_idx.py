# 데이터 처리 라이브러리
import numpy as np
import pandas as pd
import math
from datetime import datetime, timedelta
import requests
import platform
import concurrent.futures

# 데이터 수집 라이브러리
import FinanceDataReader as fdr
import yfinance as yf

# 시각화 라이브러리
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go  # [추가] ipywidgets 호환성을 위한 라이브러리

# 위젯 라이브러리
import ipywidgets as widgets
from IPython.display import display, clear_output



# 지표별 특정 기간 수익률, 주요지표, 지표별 막대 그래프 
def compare_idx():
	  
	# 1. 날짜 정의
	end_dt = pd.Timestamp.today() # 오늘 날짜 (데이터 수집 종료일)
	# [수정된 부분] 3년 전 날짜가 휴장일일 경우를 대비해 수집 시작일을 15일 정도 앞당깁니다.
	start_dt = end_dt - pd.DateOffset(years=3, days=15)

	# 2. 지수 심볼 정의
	symbol_dics = {
		'DJI':'다우존스', 'IXIC':'나스닥', 'S&P500':'S&P500', 'RUT':'러셀2000',
		'SSEC':'상해', 'HSI':'항셍', 'N225':'닛케이',
		'FTSE':'영국', 'FCHI':'프랑스', 'GDAXI':'독일',
		'KS11':'KOSPI', 'KQ11':'KOSDAQ',
		'GC=F':'금', 'HG=F':'구리', 'CL=F':'WTI', 'BTC/KRW':'비트코인'
	}

	# 3. for 문으로 순환하며 데이터 수집과 기간 수익률 계산
	results = []

	for symbol, name in symbol_dics.items():
		try:
			# S&P500의 경우 야후파이낸스 티커인 ^GSPC로 변경하여 조회 오류 방지
			fetch_symbol = '^GSPC' if symbol == 'S&P500' else symbol

			# 데이터 수집 (시작일부터 종료일까지의 종가 데이터)
			df = fdr.DataReader(fetch_symbol, start_dt, end_dt).dropna()['Close']

			if df.empty:
				continue

			# 가장 최근 날짜와 현재가
			last_date = df.index[-1]
			current_price = df.iloc[-1]

			# 특정 기준일 시점의 가격을 가져오는 내부 함수 (휴장일인 경우 직전 거래일 가격)
			def get_past_price(target_date):
				past_data = df[:target_date]
				if past_data.empty:
					return None
				return past_data.iloc[-1]

			# 수익률 계산 함수 (백분율 변환 및 소수점 2자리 반올림)
			def calc_return(past_price):
				if past_price is None or past_price == 0:
					return None
				return round(((current_price / past_price) - 1) * 100, 2)

			# 기간별 타겟 날짜 계산
			date_1m = last_date - pd.DateOffset(months=1)
			date_3m = last_date - pd.DateOffset(months=3)
			date_6m = last_date - pd.DateOffset(months=6)
			date_1y = last_date - pd.DateOffset(years=1)
			date_3y = last_date - pd.DateOffset(years=3)
			date_ytd = pd.Timestamp(year=last_date.year - 1, month=12, day=31) # 연초이후(YTD) 기준

			# 기간별 가격 추출
			price_1d = df.iloc[-2] if len(df) > 1 else None # 전일가
			price_1m = get_past_price(date_1m)
			price_3m = get_past_price(date_3m)
			price_6m = get_past_price(date_6m)
			price_1y = get_past_price(date_1y)
			price_3y = get_past_price(date_3y)
			price_ytd = get_past_price(date_ytd)

			# 데이터 적재
			results.append({
				'지수명': name,
				'1D(%)': calc_return(price_1d),
				'1M(%)': calc_return(price_1m),
				'3M(%)': calc_return(price_3m),
				'6M(%)': calc_return(price_6m),
				'YTD(%)': calc_return(price_ytd),
				'1Y(%)': calc_return(price_1y),
				'3Y(%)': calc_return(price_3y)
			})

		except Exception as e:
			print(f"[{name}] 데이터 수집 실패: {e}")

	# 4. 집계표 생성
	result_df = pd.DataFrame(results)

	# 인덱스를 지수명으로 설정하여 깔끔한 2차원 표로 변환
	result_df.set_index('지수명', inplace=True)

	# 결과 출력
	print(f"기준일: {last_date.strftime('%Y-%m-%d')} 기준 기간별 수익률 테이블\n")
	display(result_df)

	# 막대 컬러 지정 (미국, 아시아, 유럽, 한국, 원자재/코인 그룹별 색상)
	colors = ['g', 'g', 'g', 'g', 'r', 'r', 'r', 'b', 'b', 'b',  '#FFA500', '#FFA500', 'gray', 'gray' , 'gray' , 'gray']

	# 2. 그래프를 그리는 함수 정의
	def plot_returns(period):
		plt.figure(figsize=(12, 6))

		# result_df(이전 결과)에서 선택된 기간의 데이터만 추출하여 시각화용 데이터프레임(result) 생성
		# 인덱스로 있던 '지수명'을 컬럼으로 꺼냅니다.
		result = result_df[[period]].reset_index()
		result.columns = ['지수', '수익률'] # barplot 인자에 맞게 컬럼명 변경

		# barplot 함수를 사용하여 막대 그래프 생성
		# - x축: 지수명, y축: 수익률, 색상: colors에 정의된 색상, 데이터: result
		ax = sns.barplot(x='지수', y='수익률', palette=colors, data=result)

		# 차트 제목 동적 변경 (예: '1Y(%)' -> '1Y')
		period_title = period.replace('(%)', '')
		plt.title(f"지표별 {period_title} 수익률", fontsize=16, pad=15)
		plt.xlabel('')
		plt.ylabel('수익률(%)')
		plt.grid(True, axis='y', alpha=0.5)

		# [추가] 막대 위에 수익률 값(텍스트) 표시
		for p in ax.patches:
			height = p.get_height()
			if pd.notna(height): # 결측치(NaN)가 아닌 경우에만 표시
				ax.annotate(f'{height:.2f}',
							(p.get_x() + p.get_width() / 2., height),
							ha='center', # 가운데 정렬
							va='bottom' if height > 0 else 'top', # 양수면 막대 위, 음수면 막대 아래
							xytext=(0, 5 if height > 0 else -15), # 텍스트 위치 미세 조정
							textcoords='offset points',
							fontsize=9)

		plt.tight_layout()
		plt.show()

	# 3. ipywidgets 드롭다운 생성
	dropdown = widgets.Dropdown(
		options=['1D(%)', '1M(%)', '3M(%)', '6M(%)', 'YTD(%)', '1Y(%)', '3Y(%)'],
		value='1Y(%)', # 기본 선택값
		description='기간 선택:',
		disabled=False,
	)

	# 4. 위젯과 함수 연결 (인터랙티브 차트 실행)
	widgets.interact(plot_returns, period=dropdown);