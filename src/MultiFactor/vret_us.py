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



# 누적수익률, 지표, 미국주식 누적수익률
def ret_us():
	  
	# ==========================================
	# [1단계] S&P 500 종목 리스트 동적 수집
	# ==========================================
	print("S&P 500 종목 마스터 데이터를 불러오는 중입니다. 잠시만 기다려주세요...")
	url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
	html_response = requests.get(url, headers=headers).text
	sp500_table = pd.read_html(html_response)[0]

	# yfinance 티커 규칙에 맞게 변환 (예: BRK.B -> BRK-B)
	sp500_table['Symbol'] = sp500_table['Symbol'].str.replace('.', '-', regex=False)

	ticker_dict = dict(zip(sp500_table['Security'], sp500_table['Symbol']))
	stock_options = ['없음'] + sorted(sp500_table['Security'].tolist())
	clear_output() # 안내 문구 지우기

	# ==========================================
	# [2단계] 위젯 UI 생성
	# ==========================================
	# 콤보박스 5개 생성 (기본값 설정: 엔비디아, 애플)
	default_values = ['Nvidia', 'Apple Inc.', '없음', '없음', '없음']
	comboboxes = []

	for i in range(5):
		cb = widgets.Combobox(
			value=default_values[i],
			placeholder='종목명 입력 (예: Apple Inc.)',
			options=stock_options,
			description=f'종목 {i+1}:',
			ensure_option=True,
			layout=widgets.Layout(width='280px') # 영문 이름이 길어 너비를 약간 넓힘
		)
		comboboxes.append(cb)

	# 기간 선택 드롭다운
	period_selector = widgets.Dropdown(
		options=['1M', '3M', '6M', 'YTD', '1Y', '3Y'],
		value='1Y',
		description='기간 선택:',
		layout=widgets.Layout(width='200px')
	)

	# 실행 버튼
	execute_button = widgets.Button(
		description="차트 실행",
		button_style='info',
		icon='play'
	)

	# 차트 출력 영역
	out = widgets.Output()

	# ==========================================
	# [3단계] 인터랙티브 차트 생성 로직
	# ==========================================
	def update_chart(b=None):
		with out:
			clear_output(wait=True) 

			# 1. 콤보박스에서 선택된 종목 추출 (중복 및 '없음' 제거)
			selected_names = []
			for cb in comboboxes:
				if cb.value and cb.value != '없음' and cb.value in ticker_dict:
					if cb.value not in selected_names:
						selected_names.append(cb.value)

			if len(selected_names) == 0:
				print("⚠️ 분석을 진행할 종목을 최소 1개 이상 선택해주세요.")
				return

			# 2. 기간에 따른 시작일(target_dt) 계산
			end_dt = pd.Timestamp.today()
			selected_period = period_selector.value

			if selected_period == '1M': target_dt = end_dt - pd.DateOffset(months=1)
			elif selected_period == '3M': target_dt = end_dt - pd.DateOffset(months=3)
			elif selected_period == '6M': target_dt = end_dt - pd.DateOffset(months=6)
			elif selected_period == '1Y': target_dt = end_dt - pd.DateOffset(years=1)
			elif selected_period == '3Y': target_dt = end_dt - pd.DateOffset(years=3)
			elif selected_period == 'YTD': target_dt = pd.Timestamp(year=end_dt.year-1, month=12, day=31)

			start_str = target_dt.strftime('%Y-%m-%d')
			end_str = end_dt.strftime('%Y-%m-%d')

			print(f"[{selected_period}] 선택 종목의 데이터를 yfinance에서 수집 중입니다...")

			# 3. 데이터 수집 (yfinance 온디맨드 수집)
			df_list = []
			valid_names = []
			for name in selected_names:
				ticker = ticker_dict[name]
				try:
					df = yf.download(ticker, start=start_str, end=end_str, progress=False)
					
					# MultiIndex 컬럼 안전 처리
					if isinstance(df.columns, pd.MultiIndex):
						df.columns = df.columns.get_level_values(0)
						
					if not df.empty and 'Close' in df.columns:
						close_df = df[['Close']].copy()
						close_df.columns = [name]
						df_list.append(close_df)
						valid_names.append(name)
				except Exception as e:
					print(f"[{name}] 데이터 수집 실패")

			if not df_list:
				print("⚠️ 수집된 데이터가 없습니다.")
				return

			# 4. 병합 및 누적 수익률 계산
			final_df = pd.concat(df_list, axis=1)
			final_df = final_df.ffill().bfill() 
			
			cumulative_return = (final_df / final_df.iloc[0] - 1) * 100

			# 5. 차트 생성
			plt.figure(figsize=(14, 7))
			colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

			for i, column in enumerate(valid_names):
				plt.plot(cumulative_return.index, cumulative_return[column],
						color=colors[i],
						linewidth=2.5,
						label=column)

			str_start = cumulative_return.index[0].strftime('%Y-%m-%d')
			str_end = cumulative_return.index[-1].strftime('%Y-%m-%d')

			plt.title(f'S&P 500 종목 누적 수익률 비교 ({str_start} ~ {str_end})', fontsize=16, fontweight='bold', pad=15)
			plt.ylabel('누적 수익률 (%)', fontsize=12)
			plt.axhline(0, color='black', linewidth=1, linestyle='--')
			plt.grid(True, linestyle='--', alpha=0.5)
			plt.legend(loc='upper left', fontsize=11, frameon=True, shadow=True)
			plt.xticks(fontsize=10)
			plt.yticks(fontsize=10)

			plt.tight_layout()
			plt.show()

	# 버튼 이벤트 연결
	execute_button.on_click(update_chart)

	# ==========================================
	# [4단계] UI 레이아웃 배치 및 출력
	# ==========================================
	ui_controls = widgets.HBox([period_selector, execute_button])
	ui_combos_1 = widgets.HBox(comboboxes[:3])
	ui_combos_2 = widgets.HBox(comboboxes[3:])

	display(widgets.VBox([ui_controls, ui_combos_1, ui_combos_2, out]))

	# 최초 1회 자동 실행
	update_chart()