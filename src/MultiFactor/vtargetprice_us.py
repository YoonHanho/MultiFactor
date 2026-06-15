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



# 목표가, 미국주식
def targetprice_us():

	# ==========================================
	# [1단계] S&P 500 종목 리스트 수집
	# ==========================================
	print("S&P 500 종목 마스터 데이터를 불러오는 중입니다...")
	url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
	#html_response = requests.get(url, headers=headers).text
	#sp500_table = pd.read_html(html_response)[0]
	sp500_table = pd.read_html(url, storage_options=headers)[0]

	sp500_table['Symbol'] = sp500_table['Symbol'].str.replace('.', '-', regex=False)
	tickers = sp500_table['Symbol'].tolist()
	names = dict(zip(sp500_table['Symbol'], sp500_table['Security']))
	sectors = dict(zip(sp500_table['Symbol'], sp500_table['GICS Sector']))
	clear_output()

	# ==========================================
	# [2단계] UI 위젯 구성
	# ==========================================
	count_selector = widgets.Dropdown(
		options=[('시가총액 상위 100개만 (빠름)', 100), ('S&P 500 전체 (약 30~60초 소요)', 500)],
		value=100,
		description='검색 범위:'
	)

	# [수정 3] 출력 컬럼(행)수 지정 드롭박스 추가
	row_count_selector = widgets.Dropdown(
		options=[10, 20, 30, 40, 50],
		value=20, # 기본값 20개
		description='출력 개수:',
		layout=widgets.Layout(width='180px')
	)

	execute_button = widgets.Button(
		description="괴리율 분석 실행",
		button_style='success',
		icon='search'
	)

	out = widgets.Output()

	# ==========================================
	# [3단계] 단일 종목 목표가 추출 함수 (멀티스레딩용)
	# ==========================================
	def fetch_target_info(ticker):
		try:
			info = yf.Ticker(ticker).info
			
			current_price = info.get('currentPrice')
			target_mean = info.get('targetMeanPrice')
			target_high = info.get('targetHighPrice')
			rec_mean = info.get('recommendationMean')
			num_analysts = info.get('numberOfAnalystOpinions', 0)
			
			if current_price is None or target_mean is None:
				return None
				
			upside_gap = ((target_mean - current_price) / current_price) * 100
			
			# [수정 1] 반환되는 딕셔너리의 키값을 모두 한글로 변경
			return {
				'종목코드': ticker,
				'종목명': names.get(ticker, ticker),
				'섹터': sectors.get(ticker, 'Unknown'),
				'현재가($)': round(current_price, 2),
				'목표가(평균)': round(target_mean, 2),
				'최고목표가': round(target_high, 2),
				'괴리율(%)': round(upside_gap, 2),
				'추천점수(1=매수)': round(rec_mean, 2) if rec_mean else None,
				'애널리스트수': num_analysts
			}
		except Exception:
			return None

	# ==========================================
	# [4단계] 데이터 병렬 수집 및 결과 출력 로직
	# ==========================================
	def run_screener(b=None):
		with out:
			clear_output(wait=True)
			limit = count_selector.value
			display_count = row_count_selector.value # 드롭박스에서 선택한 출력 개수 가져오기
			
			target_tickers = tickers[:limit]
			
			print(f"총 {limit}개 종목의 애널리스트 목표가 데이터를 수집 중입니다. 잠시만 기다려주세요...")
			
			results = []
			with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
				futures = [executor.submit(fetch_target_info, t) for t in target_tickers]
				
				for future in concurrent.futures.as_completed(futures):
					data = future.result()
					if data is not None:
						results.append(data)
						
			if not results:
				print("데이터를 불러오지 못했습니다.")
				return
				
			df = pd.DataFrame(results)
			
			# [수정 1] 한글 컬럼명에 맞춰 필터링 조건 업데이트
			filtered_df = df[
				(df['애널리스트수'] >= 5) & 
				(df['추천점수(1=매수)'] <= 2.5) &
				(df['괴리율(%)'] > 0)
			]
			
			sorted_df = filtered_df.sort_values(by='괴리율(%)', ascending=False).reset_index(drop=True)
			
			print("✅ 수집 및 분석 완료!\n")
			print("💡 [추천점수]는 1.0(강력매수) ~ 5.0(매도)를 의미하며, 낮을수록 좋습니다.")
			print(f"📊 목표가 괴리율(상승 여력) 상위 {display_count}개 종목:")
			
			# [수정 2] format() 메서드를 사용하여 수치형 데이터를 무조건 소수점 둘째 자리까지 출력
			styled_output = (
				sorted_df.head(display_count).style
				.background_gradient(subset=['괴리율(%)'], cmap='Greens')
				.background_gradient(subset=['추천점수(1=매수)'], cmap='Blues_r')
				.format({
					'현재가($)': "{:.2f}",
					'목표가(평균)': "{:.2f}",
					'최고목표가': "{:.2f}",
					'괴리율(%)': "{:.2f}",
					'추천점수(1=매수)': "{:.2f}"
				})
			)
			
			display(styled_output)

	# 버튼 이벤트 연결
	execute_button.on_click(run_screener)

	# [수정 3] UI 출력 HBox에 row_count_selector 추가
	display(widgets.HBox([count_selector, row_count_selector, execute_button]), out)