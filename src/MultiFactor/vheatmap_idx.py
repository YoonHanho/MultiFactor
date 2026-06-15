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



#블룸버그 히트맵, 지수 
def heatmap_idx():

	# 2. 날짜 지정 (5년 전의 전년도 12월 1일 계산)
	end_dt = pd.Timestamp.today()
	start_year = end_dt.year - 5 - 1 # 현재 연도에서 6년 전
	start_dt = f"{start_year}-12-01"

	# 3. 심볼 정의 (드롭다운 매핑을 위해 Key-Value 위치 조정)
	dropdown_options = {
		'다우존스':'DJI', '나스닥':'IXIC', 'S&P500':'S&P500', '러셀2000':'RUT',
		'상해':'SSEC', '항셍':'HSI', '닛케이':'N225',
		'영국':'FTSE', '프랑스':'FCHI', '독일':'GDAXI',
		'KOSPI':'KS11', 'KOSDAQ':'KQ11',
		'금':'GC=F', '구리':'HG=F', 'WTI':'CL=F', '비트코인':'BTC/KRW'
	}

	# 4. 히트맵 생성 함수
	# 4. 히트맵 생성 함수 (Pandas 구버전 호환용으로 수정됨)
	def get_heatmap(df, title, colorset='KR'):
		# 날짜 인덱스를 데이터프레임 컬럼으로 생성
		if df.index.name == 'Date' or isinstance(df.index, pd.DatetimeIndex):
			df = df.reset_index()

		# 컬럼명 변경 : 날짜(BAS_DT), 종가(CLOSE)
		df.columns = ['BAS_DT', 'CLOSE']
		df['BAS_DT'] = pd.to_datetime(df['BAS_DT'])

		# [수정됨] 월별 마지막 종가 추출 및 수익률 계산 (freq='ME' -> freq='M')
		#monthly_close = df.groupby(pd.Grouper(key='BAS_DT', freq='M'))['CLOSE'].last()
		# 로컬(최신버전)과 Colab(구버전) 호환용 코드
		try:
			monthly_close = df.groupby(pd.Grouper(key='BAS_DT', freq='ME'))['CLOSE'].last()
		except ValueError:
			monthly_close = df.groupby(pd.Grouper(key='BAS_DT', freq='M'))['CLOSE'].last()
		
		monthly_ret = ((monthly_close / monthly_close.shift(1)) - 1) * 100
		monthly_ret.dropna(inplace=True)

		# 데이터프레임 변환 및 피벗 테이블 생성
		data = monthly_ret.to_frame()
		data['year'] = monthly_ret.index.year
		data['month'] = monthly_ret.index.month
		table = pd.pivot_table(data=data, values='CLOSE', index='month', columns='year')

		# [수정됨] 연간 마지막 종가 추출 및 수익률 계산 (freq='YE' -> freq='Y')
		#yearly_close = df.groupby(pd.Grouper(key='BAS_DT', freq='Y'))['CLOSE'].last()
		try:
			yearly_close = df.groupby(pd.Grouper(key='BAS_DT', freq='YE'))['CLOSE'].last()
		except ValueError:
			yearly_close = df.groupby(pd.Grouper(key='BAS_DT', freq='Y'))['CLOSE'].last()
		
		yearly_ret = ((yearly_close / yearly_close.shift(1)) - 1) * 100
		yearly_ret.dropna(inplace=True)

		data_y = yearly_ret.to_frame()
		data_y.index = data_y.index.year

		# 행/열 결합 및 인덱스 정리
		r1 = pd.concat([table, data_y.T], axis=0, ignore_index=True)
		r2 = pd.concat([r1, r1.mean(axis=1).to_frame()], axis=1, ignore_index=True)

		r2.index = list(np.arange(1, 13, 1)) + ['Yearly']
		r2.columns = list(table.columns) + ['Avg']

		# 그래프 생성
		plt.figure(figsize=(12, 10))

		# 컬러셋 설정
		if colorset == 'US':
			cmap = mcolors.ListedColormap(['#DF253E', '#F4292F', '#146723', '#00C630'])
		elif colorset == 'KR':
			cmap = mcolors.ListedColormap(['#2D5FDD', '#B3D7F8', '#FCEBEB', '#DA0000'])

		bounds = [-100, -1, 0, 1, 100]
		norm = mcolors.BoundaryNorm(bounds, cmap.N)

		# 히트맵 그리기
		ax = sns.heatmap(r2, cmap=cmap, norm=norm, annot=True, linewidth=.2, fmt='.2f',
						vmin=-100, vmax=100, cbar=False, annot_kws={"size": 13, "fontweight": 'bold'})

		# 세부 서식 지정
		ax.set(xlabel='', ylabel='')
		ax.xaxis.set_tick_params(labelsize=12)
		ax.yaxis.set_tick_params(labelsize=12)
		ax.xaxis.tick_top()

		plt.title(title, fontsize=18, fontweight='bold', pad=30)
		plt.xticks(fontsize=13, fontweight='bold', rotation=0)
		plt.yticks(fontsize=13, fontweight='bold', rotation=0)

		plt.tight_layout()
		plt.show()




	# 5. ipywidgets UI 및 인터랙티브 로직 설정
	index_selector = widgets.Dropdown(
		options=list(dropdown_options.keys()),
		value='KOSPI',
		description='지수 선택:',
	)

	color_selector = widgets.Dropdown(
		options=['KR', 'US'],
		value='KR',
		description='컬러셋:',
	)

	out = widgets.Output()

	# 데이터 재조회 방지를 위한 캐시 딕셔너리
	data_cache = {}

	def update_dashboard(*args):
		with out:
			clear_output(wait=True)

			selected_name = index_selector.value
			selected_symbol = dropdown_options[selected_name]
			selected_color = color_selector.value

			# 캐시에 데이터가 없으면 API에서 수집
			if selected_symbol not in data_cache:
				print(f"[{selected_name}] ({start_dt} ~ 현재) 데이터를 수집 중입니다. 잠시만 기다려주세요...")

				# S&P500의 경우 야후파이낸스 조회를 위해 티커 변경
				fetch_symbol = '^GSPC' if selected_symbol == 'S&P500' else selected_symbol

				try:
					df = fdr.DataReader(fetch_symbol, start_dt, end_dt)[['Close']]
					data_cache[selected_symbol] = df
					clear_output(wait=True)
				except Exception as e:
					clear_output(wait=True)
					print(f"[{selected_name}] 데이터 수집에 실패했습니다. 에러 로그: {e}")
					return

			# 캐시된 데이터 복사 후 차트 생성
			df_target = data_cache[selected_symbol].copy()

			if df_target.empty:
				print(f"[{selected_name}] 해당 기간의 데이터가 존재하지 않습니다.")
				return

			chart_title = f"{selected_name} 최근 5년 월별 수익률 히트맵 (%)"
			get_heatmap(df_target, title=chart_title, colorset=selected_color)

	# 위젯 값 변경 시 이벤트 연결
	index_selector.observe(update_dashboard, names='value')
	color_selector.observe(update_dashboard, names='value')

	# UI 가로 배치 및 출력
	ui = widgets.HBox([index_selector, color_selector])
	display(ui, out)

	# 초기 실행
	update_dashboard()    