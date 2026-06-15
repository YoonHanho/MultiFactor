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



# 누적수익률, 지표, 지표별 누적수익률 
def ret_idx():
	  
	# ==========================================
	# [1단계] 데이터 최초 1회 수집 (3년치 전체)
	# ==========================================
	print("데이터를 수집 중입니다. 잠시만 기다려주세요...")

	end_dt = pd.Timestamp.today()
	start_dt = end_dt - pd.DateOffset(years=3, days=15)

	symbol_dics = {
		'DJI':'다우존스', 'IXIC':'나스닥', 'S&P500':'S&P500', 'RUT':'러셀2000',
		'SSEC':'상해', 'HSI':'항셍', 'N225':'닛케이',
		'FTSE':'영국', 'FCHI':'프랑스', 'GDAXI':'독일',
		'KS11':'KOSPI', 'KQ11':'KOSDAQ',
		'GC=F':'금', 'HG=F':'구리', 'CL=F':'WTI', 'BTC/KRW':'비트코인'
	}

	df_list = []
	for ticker, name in symbol_dics.items():
		try:
			# S&P500 티커 오류 방지
			fetch_symbol = '^GSPC' if ticker == 'S&P500' else ticker
			df = fdr.DataReader(fetch_symbol, start_dt, end_dt)[['Close']]
			df.columns = [name]
			df_list.append(df)
		except Exception as e:
			print(f"[{name}] 수집 실패")

	# 모든 데이터를 하나의 데이터프레임으로 병합 및 결측치 보정 (최신 Pandas 문법 적용)
	final_df = pd.concat(df_list, axis=1)
	final_df = final_df.ffill().bfill()

	print("✅ 데이터 수집 완료!\n")

	# ==========================================
	# [2단계] 인터랙티브 차트 생성 로직
	# ==========================================
	# 라인 색상 정의
	colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#000080', '#d62728', '#e377c2']

	# 위젯 UI 생성
	indices_selector = widgets.SelectMultiple(
		options=list(symbol_dics.values()),
		value=['나스닥', 'S&P500', 'KOSPI'], # 기본 선택값
		description='지수 선택:',
		disabled=False,
		layout=widgets.Layout(height='120px')
	)

	period_selector = widgets.Dropdown(
		options=['1M', '3M', '6M', 'YTD', '1Y', '3Y'],
		value='1Y',
		description='기간 선택:',
		disabled=False,
	)

	# 차트가 그려질 출력 영역
	out = widgets.Output()

	# 차트 업데이트 함수
	def update_chart(*args):
		with out:
			clear_output(wait=True) # 기존 차트 지우기

			selected_indices = list(indices_selector.value)
			selected_period = period_selector.value

			# 1. 지수 선택 개수 제한 (최대 5개)
			if len(selected_indices) == 0:
				print("⚠️ 최소 1개 이상의 지수를 선택해주세요.")
				return
			elif len(selected_indices) > 5:
				print("⚠️ 최대 5개까지만 선택 가능합니다. 상위 5개만 표시됩니다.")
				selected_indices = selected_indices[:5]

			# 2. 선택된 기간에 따른 시작일(target_dt) 계산
			last_date = final_df.index[-1]

			if selected_period == '1M': target_dt = last_date - pd.DateOffset(months=1)
			elif selected_period == '3M': target_dt = last_date - pd.DateOffset(months=3)
			elif selected_period == '6M': target_dt = last_date - pd.DateOffset(months=6)
			elif selected_period == '1Y': target_dt = last_date - pd.DateOffset(years=1)
			elif selected_period == '3Y': target_dt = last_date - pd.DateOffset(years=3)
			elif selected_period == 'YTD': target_dt = pd.Timestamp(year=last_date.year-1, month=12, day=31)

			# 3. 데이터 자르기(Slicing) 및 누적 수익률 계산
			# 기간에 해당하는 데이터만 추출
			sliced_df = final_df.loc[target_dt:, selected_indices]

			# 추출된 기간의 첫 번째 날짜 가격을 기준으로 누적 수익률 계산
			if not sliced_df.empty:
				cumulative_return = (sliced_df / sliced_df.iloc[0] - 1) * 100
			else:
				print("해당 기간의 데이터가 없습니다.")
				return

			# 4. 차트 생성
			plt.figure(figsize=(14, 7))

			for i, column in enumerate(cumulative_return.columns):
				plt.plot(cumulative_return.index, cumulative_return[column],
						color=colors[i],
						linewidth=2.5, # 가독성을 위해 두께 2.5로 조정
						label=column)

			# 시작일과 종료일을 YYYY-MM-DD 형식으로 변환
			str_start = cumulative_return.index[0].strftime('%Y-%m-%d')
			str_end = cumulative_return.index[-1].strftime('%Y-%m-%d')

			plt.title(f'글로벌 자산 누적 수익률 비교 ({str_start} ~ {str_end})', fontsize=16, fontweight='bold', pad=15)
			plt.ylabel('누적 수익률 (%)', fontsize=12)
			plt.axhline(0, color='black', linewidth=1, linestyle='--') # 수익률 0% 기준선 추가
			plt.grid(True, linestyle='--', alpha=0.5)
			plt.legend(loc='upper left', fontsize=11, frameon=True, shadow=True)
			plt.xticks(fontsize=10)
			plt.yticks(fontsize=10)

			plt.tight_layout()
			plt.show()

	# 위젯 값 변경 시 update_chart 함수 호출되도록 연결
	indices_selector.observe(update_chart, names='value')
	period_selector.observe(update_chart, names='value')

	# UI 배치 (가로로 위젯 배치)
	ui = widgets.HBox([indices_selector, period_selector])

	# 최초 1회 차트 강제 실행
	update_chart()

	# 위젯과 출력 영역 표시
	display(widgets.HTML("<b>💡 지수 다중 선택 방법:</b> <code>Ctrl</code>(윈도우) 또는 <code>Cmd</code>(맥) 키를 누른 상태로 클릭하세요. (최대 5개)"))
	display(ui, out)
