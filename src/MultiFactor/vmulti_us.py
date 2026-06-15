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



# 개별 복합 차트, 미국주식, 지수별 개별 라인 차트 
def multi_us():

	# 1. S&P 500 종목명 및 티커 동적 수집 (위키피디아 테이블 활용)
	url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

	# [수정된 부분] 일반 브라우저인 것처럼 User-Agent 헤더를 추가하여 403 에러 방지
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
	html_response = requests.get(url, headers=headers).text
	sp500_table = pd.read_html(html_response)[0]

	# yfinance는 버크셔해서웨이(BRK.B) 같은 티커의 '.'을 '-'로 치환해야 인식합니다.
	sp500_table['Symbol'] = sp500_table['Symbol'].str.replace('.', '-', regex=False)

	# 기업명(Security)을 키로, 티커(Symbol)를 값으로 갖는 딕셔너리 생성
	ticker_dict = dict(zip(sp500_table['Security'], sp500_table['Symbol']))
	stock_options = ['없음'] + sorted(sp500_table['Security'].tolist())

	# 2. 날짜 위젯 구성
	today = datetime.today()
	three_years_ago = today - timedelta(days=1095)

	start_date_picker = widgets.DatePicker(
		description='시작일',
		value=three_years_ago.date()
	)
	end_date_picker = widgets.DatePicker(
		description='종료일',
		value=today.date()
	)

	# 3. 콤보박스 위젯 구성
	#default_values = ['Apple Inc.', 'Microsoft Corporation', 'NVIDIA Corporation', '없음', '없음', '없음']
	default_values = ['Nvidia', 'Apple Inc.', '없음', '없음', '없음', '없음']
	comboboxes = []

	for i in range(6):
		cb = widgets.Combobox(
			value=default_values[i],
			placeholder='종목명 입력 (예: Apple Inc.)',
			options=stock_options,
			description=f'종목 {i+1}:',
			ensure_option=True,
			disabled=False
		)
		comboboxes.append(cb)

	# 4. 실행 버튼 생성
	execute_button = widgets.Button(
		description='차트 실행',
		button_style='primary',
		icon='play'
	)

	out = widgets.Output()

	# 5. 버튼 클릭 시 실행될 콜백 함수
	def update_charts(b=None):
		selected_names = []
		for cb in comboboxes:
			if cb.value and cb.value != '없음' and cb.value in ticker_dict:
				if cb.value not in selected_names:
					selected_names.append(cb.value)
		
		start_dt = start_date_picker.value.strftime('%Y-%m-%d')
		end_dt = end_date_picker.value.strftime('%Y-%m-%d')
		
		with out:
			clear_output(wait=True)
			
			num_stocks = len(selected_names)
			if num_stocks == 0:
				print("분석을 진행할 종목을 최소 1개 이상 선택해주세요.")
				return
			
			rows = 1 if num_stocks <= 3 else 2
			cols = 3
			
			fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows))
			axes_flat = axes.flatten() if rows == 2 else axes
			
			for i in range(rows * cols):
				if i < num_stocks:
					name = selected_names[i]
					ticker = ticker_dict[name]
					try:
						df = yf.download(ticker, start=start_dt, end=end_dt, progress=False)
						
						if isinstance(df.columns, pd.MultiIndex):
							df.columns = df.columns.get_level_values(0)
							
						if df.empty:
							raise ValueError("Data Empty")
						
						# 거래량 막대그래프
						ax_vol = axes_flat[i].twinx()
						ax_vol.bar(df.index, df['Volume'], color='tab:gray', alpha=0.3)
						ax_vol.set_ylim(0, df['Volume'].max() * 4) 
						ax_vol.set_yticks([]) 
						
						# 주가 선그래프
						df['Close'].plot(kind='line', ax=axes_flat[i], color='tab:blue', linewidth=1.5)
						axes_flat[i].set_title(f"{name} ({ticker})", fontsize=11, fontweight='bold')
						axes_flat[i].grid(True, axis='y', linestyle='--', alpha=0.5)
						axes_flat[i].set_xlabel('')
						axes_flat[i].set_ylabel('')
						
						axes_flat[i].set_zorder(ax_vol.get_zorder() + 1)
						axes_flat[i].patch.set_visible(False)
						
					except Exception as e:
						axes_flat[i].set_title(f"{name} (로드 실패)", fontsize=11)
						axes_flat[i].text(0.5, 0.5, f"Data Error\n({ticker})", ha='center', va='center')
				else:
					axes_flat[i].axis('off')
			
			plt.tight_layout()
			plt.show()

	# 6. 버튼에 이벤트 리스너 연결
	execute_button.on_click(update_charts)

	# 7. UI 레이아웃 조립 및 출력
	ui = widgets.VBox([
		widgets.HBox([start_date_picker, end_date_picker, execute_button]),
		widgets.HBox(comboboxes[:3]),
		widgets.HBox(comboboxes[3:]),
		out
	])

	display(ui)
	update_charts()