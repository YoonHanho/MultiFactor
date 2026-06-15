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



# 실적재무 종합, 국내주식, 개별종목 실적 및 밸류 추이 
def finance_kr():

	# 1. 주식종목 정보 수집
	stocks = (fdr.StockListing('KRX')
			  .query("Market.isin(['KOSPI','KOSDAQ'])")
			  .reset_index(drop=True))[['Name', 'Code']]

	# 2. 메인 시각화 함수 (기간 옵션 YQ 추가)
	def plot_multi_factor(stock_name, YQ='Y'):
		stock_code = stocks.loc[stocks['Name'] == stock_name, 'Code'].values[0]

		# --- [1] 모멘텀 지표: 최근 1년 주가 및 거래량 차트 ---
		end_dt = datetime.today()
		start_dt = end_dt - timedelta(days=365)
		df = fdr.DataReader(stock_code, start_dt.strftime('%Y%m%d'), end_dt.strftime('%Y%m%d'))

		fig_mom, (ax_price, ax_vol) = plt.subplots(2, 1, figsize=(14, 6), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

		ax_price.plot(df.index, df['Close'], color='tab:blue', linewidth=2)
		ax_price.set_title(f"[{stock_name}] 모멘텀 지표 (최근 1년 주가 및 거래량)", fontsize=15, fontweight='bold')
		ax_price.grid(True, axis='y', linestyle='--', alpha=0.7)
		ax_price.set_ylabel('주가(원)')

		ax_vol.bar(df.index, df['Volume'], color='tab:gray', alpha=0.5)
		ax_vol.grid(True, axis='y', linestyle='--', alpha=0.7)
		ax_vol.set_ylabel('거래량')

		plt.tight_layout()
		plt.show()

		# --- [2] 밸류 & 퀄리티 지표: 재무 데이터 막대그래프 ---
		try:
			# 연간(Y) 또는 분기(Q) 재무제표 동적 수집
			fs = fdr.SnapDataReader(f'NAVER/FINSTATE-{YQ}/{stock_code}')
			period_text = "연간" if YQ == 'Y' else "분기"

			cols = ['PER(배)', 'PBR(배)', 'ROE(%)', '매출액', '영업이익', '당기순이익']
			res = fs[cols].T.dropna(axis=1, how='all')
			res.columns = [x.strftime('%y-%m') for x in res.columns]

			fig_vq, axes = plt.subplots(2, 3, figsize=(14, 8), tight_layout=True)
			fig_vq.suptitle(f"[{stock_name}] 밸류 & 퀄리티 지표 ({period_text} 재무제표)", fontsize=15, fontweight='bold', y=1.02)
			axes = axes.flatten()

			for i, metric in enumerate(cols):
				ax = axes[i]
				if metric in res.index:
					data = res.loc[metric].dropna()
					if not data.empty:
						ymin = data.min() * 0.9 if data.min() > 0 else abs(data.min()) * -1.1
						sns.barplot(x=data.index, y=data.values, ax=ax, palette='Blues_r' if i < 2 else 'Greens_r')
						ax.set_ylim(ymin, None)

				ax.set_title(metric, fontsize=12)
				ax.set_xlabel('')
				ax.grid(True, axis='y', linestyle='--', alpha=0.7)
				ax.tick_params(axis='x', rotation=45)

			plt.show()

		except Exception as e:
			print(f"재무 데이터를 불러오는 중 오류가 발생했습니다: {e}")

	# 3. ipywidgets 구성
	# 종목명 입력 콤보박스
	stock_input = widgets.Combobox(
		placeholder='종목명 입력 (예: 삼성전자)',
		options=stocks['Name'].tolist(),
		description='종목 검색:',
		ensure_option=True,
		disabled=False
	)

	# 연간/분기 선택 드롭다운 (기본값 'Y')
	period_dropdown = widgets.Dropdown(
		options=[('연간', 'Y'), ('분기', 'Q')],
		value='Y',
		description='재무 기준:',
		disabled=False,
	)

	out = widgets.Output()

	# 값이 변경될 때마다 실행될 통합 콜백 함수
	def update_charts(change):
		stock_name = stock_input.value
		yq_period = period_dropdown.value

		# 종목명이 정확히 입력된 경우에만 차트 렌더링
		if stock_name in stocks['Name'].values:
			with out:
				clear_output(wait=True)
				plot_multi_factor(stock_name, YQ=yq_period)

	# 위젯에 이벤트 리스너 연결 (어떤 것을 바꾸든 업데이트 트리거)
	stock_input.observe(update_charts, names='value')
	period_dropdown.observe(update_charts, names='value')

	# HBox를 사용하여 위젯을 가로로 깔끔하게 배치
	ui = widgets.HBox([stock_input, period_dropdown])
	display(ui, out)