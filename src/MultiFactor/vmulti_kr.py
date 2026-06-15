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


# 개별 복합 차트, 국내주식, 지수별 개별 라인 차트 
def multi_kr():

	# 1. 종목명 및 코드 수집
	stocks = (fdr.StockListing('KRX')
			  .query("Market.isin(['KOSPI','KOSDAQ'])")
			  .reset_index(drop=True))[['Name', 'Code']]

	ticker_dict = dict(zip(stocks['Name'], stocks['Code']))
	stock_options = ['없음'] + stocks['Name'].tolist()

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
	default_values = ['삼성전자', 'SK하이닉스', '없음', '없음', '없음', '없음']
	comboboxes = []

	for i in range(6):
		cb = widgets.Combobox(
			value=default_values[i],
			placeholder='종목명 입력 (예: 삼성전자)',
			options=stock_options,
			description=f'종목 {i+1}:',
			ensure_option=True,
			disabled=False
		)
		comboboxes.append(cb)

	# 4. 실행 버튼 생성
	execute_button = widgets.Button(
		description='차트 실행',
		button_style='primary', # 파란색 강조 버튼
		icon='play'             # 재생 아이콘 추가
	)

	out = widgets.Output()

	# 5. 버튼 클릭 시 실행될 콜백 함수
	def update_charts(b=None):
		selected_names = []
		for cb in comboboxes:
			if cb.value and cb.value != '없음' and cb.value in ticker_dict:
				if cb.value not in selected_names:
					selected_names.append(cb.value)
		
		start_dt = start_date_picker.value
		end_dt = end_date_picker.value
		
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
						# 데이터 수집 (거래량 포함)
						df = fdr.DataReader(ticker, start_dt, end_dt)[['Close', 'Volume']]
						
						# 보조축(twinx)을 활용한 거래량 막대그래프 
						ax_vol = axes_flat[i].twinx()
						ax_vol.bar(df.index, df['Volume'], color='tab:gray', alpha=0.3)
						ax_vol.set_ylim(0, df['Volume'].max() * 4) 
						ax_vol.set_yticks([]) 
						
						# 주가 선그래프
						df['Close'].plot(kind='line', ax=axes_flat[i], color='tab:blue', linewidth=1.5)
						axes_flat[i].set_title(name, fontsize=12, fontweight='bold')
						axes_flat[i].grid(True, axis='y', linestyle='--', alpha=0.5)
						axes_flat[i].set_xlabel('')
						axes_flat[i].set_ylabel('')
						
						axes_flat[i].set_zorder(ax_vol.get_zorder() + 1)
						axes_flat[i].patch.set_visible(False)
						
					except Exception as e:
						axes_flat[i].set_title(f"{name} (데이터 로드 실패)")
						axes_flat[i].text(0.5, 0.5, "Data Not Found", ha='center', va='center')
				else:
					axes_flat[i].axis('off')
			
			plt.tight_layout()
			plt.show()

	# 6. 버튼에 이벤트 리스너 연결 (기존 observe 제거, on_click 추가)
	execute_button.on_click(update_charts)

	# 7. UI 레이아웃 조립 및 출력
	ui = widgets.VBox([
		widgets.HBox([start_date_picker, end_date_picker, execute_button]), # 실행 버튼을 날짜 옆에 배치
		widgets.HBox(comboboxes[:3]),
		widgets.HBox(comboboxes[3:]),
		out
	])

	# 초기 뷰어 렌더링
	display(ui)
	# update_charts() # 시작 시 자동 실행을 원치 않으시면 이 줄은 삭제/주석 처리해도 됩니다. (현재는 활성화해둠)
	update_charts()