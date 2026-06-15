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


# 업종목 트리맵, 미국주식, 시가상위종목 주가 등락률 트리맵 
def treemap_us():

	# ==========================================
	# [1단계] S&P 500 메타데이터 동적 수집 (위키피디아)
	# ==========================================
	print("S&P 500 메타데이터를 수집 중입니다. (티커, 섹터 정보)")
	url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
	html_response = requests.get(url, headers=headers).text
	sp500_table = pd.read_html(html_response)[0]

	# yfinance 티커 규칙 치환
	sp500_table['Symbol'] = sp500_table['Symbol'].str.replace('.', '-', regex=False)

	meta_df = sp500_table[['Symbol', 'Security', 'GICS Sector']].copy()
	meta_df.columns = ['Ticker', 'Name', 'Sector']
	clear_output()

	# ==========================================
	# [2단계] 위젯 UI 구성
	# ==========================================
	today = datetime.today()
	if today.weekday() == 0: # 월요일이면 지난주 금요일
		default_date = today - timedelta(days=3)
	elif today.weekday() == 6: # 일요일이면 지난주 금요일
		default_date = today - timedelta(days=2)
	else:
		default_date = today - timedelta(days=1)

	date_picker = widgets.DatePicker(
		description='기준 일자',
		value=default_date.date(),
		layout=widgets.Layout(width='250px')
	)

	top_n_selector = widgets.Dropdown(
		options=[('상위 100개 종목', 100), 
				('상위 200개 종목', 200), 
				('상위 300개 종목', 300), 
				('상위 400개 종목', 400), 
				('S&P 500 전체', 505)],
		value=100,
		description='분석 종목수:',
		layout=widgets.Layout(width='250px')
	)

	execute_button = widgets.Button(
		description="트리맵 생성",
		button_style='info',
		icon='play',
		layout=widgets.Layout(width='150px')
	)

	out = widgets.Output()

	# ==========================================
	# [3단계] 데이터 수집 및 트리맵 렌더링 (초고속 버전)
	# ==========================================
	def generate_treemap(b=None):
		with out:
			clear_output(wait=True)
			
			target_date_str = date_picker.value.strftime('%Y-%m-%d')
			top_n = top_n_selector.value
			
			print(f"[{target_date_str}] 기준, 데이터를 yfinance에서 일괄 수집 중입니다. (약 3~5초 소요)")
			
			start_fetch_dt = (date_picker.value - timedelta(days=7)).strftime('%Y-%m-%d')
			end_fetch_dt = (date_picker.value + timedelta(days=1)).strftime('%Y-%m-%d')
			tickers_str = " ".join(meta_df['Ticker'].tolist())
			
			try:
				# 500개 종목의 주가 및 거래량 데이터를 '한 번에' 다운로드
				raw_data = yf.download(tickers_str, start=start_fetch_dt, end=end_fetch_dt, progress=False)
				
				if raw_data.empty:
					raise ValueError("해당 기간의 데이터를 찾을 수 없습니다.")
					
				# yfinance 최신 버전의 MultiIndex 컬럼 안전 처리
				if isinstance(raw_data.columns, pd.MultiIndex):
					try:
						close_prices = raw_data.xs('Close', level=0, axis=1)
						volumes = raw_data.xs('Volume', level=0, axis=1)
					except KeyError:
						close_prices = raw_data.xs('Close', level=1, axis=1)
						volumes = raw_data.xs('Volume', level=1, axis=1)
				else:
					close_prices = raw_data['Close']
					volumes = raw_data['Volume']
					
				if len(close_prices) < 2:
					print("⚠️ 선택한 날짜 주변에 충분한 거래일 데이터(최소 2일)가 없습니다.")
					return
					
				current_close = close_prices.iloc[-1]
				prev_close = close_prices.iloc[-2]
				current_volume = volumes.iloc[-1]
				
				# 수익률 계산 (%)
				returns = ((current_close - prev_close) / prev_close) * 100
				
				# [핵심] 시가총액을 개별 조회하는 대신, '일일 거래대금(종가 * 거래량)'을 규모 대용치로 사용
				trading_value = current_close * current_volume
				
				df = pd.DataFrame({
					'Ticker': current_close.index,
					'Return': returns.values,
					'TradingValue': trading_value.values
				})
				
				# 결측치 제거 및 메타데이터 병합
				df = df.dropna()
				df = df.merge(meta_df, on='Ticker', how='inner')
				
				# 거래대금 규모 순으로 정렬 후 사용자가 선택한 Top N 추출
				df = df[df['TradingValue'] > 0].sort_values(by='TradingValue', ascending=False).head(top_n)
				
				# 트리맵 면적을 위한 로그 변환
				df['Size_Log'] = np.log1p(df['TradingValue'])
				
				# 커스텀 컬러맵 (파랑=하락, 흰색=보합, 빨강=상승)
				custom_colorscale = [
					[0.0, "rgb(44, 95, 233)"],   
					[0.4, "rgb(151, 185, 255)"], 
					[0.5, "rgb(255, 255, 255)"], 
					[0.6, "rgb(255, 165, 165)"], 
					[1.0, "rgb(235, 41, 41)"]    
				]
				
				# 트리맵 생성
				fig = px.treemap(
					df,
					path=['Sector', 'Ticker'], 
					values='Size_Log',    
					color='Return',            
					color_continuous_scale=custom_colorscale,
					color_continuous_midpoint=0, 
					title=f'S&P 500 시장 규모 상위 {top_n}개 업종/종목별 등락률 ({close_prices.index[-1].strftime("%Y-%m-%d")} 기준)',
					hover_data={'Return': ':.2f', 'Size_Log': False, 'TradingValue': False, 'Name': True} 
				)
				
				fig.update_layout(
					width=1000, 
					height=700, 
					title_font_size=16,
					title_font_family="Malgun Gothic",
					margin=dict(t=50, l=10, r=10, b=10)
				)
				
				clear_output(wait=True)
				
				# [핵심 변경 사항] fig.show() 대신 FigureWidget으로 감싸서 display() 호출
				fig_widget = go.FigureWidget(fig)
				display(fig_widget)
				
			except Exception as e:
				clear_output(wait=True)
				print(f"데이터 처리 중 오류가 발생했습니다: {e}")

	# 이벤트 연결
	execute_button.on_click(generate_treemap)

	# UI 레이아웃
	ui = widgets.HBox([date_picker, top_n_selector, execute_button])
	display(ui, out)

	print("✅ 준비 완료! '트리맵 생성' 버튼을 클릭해보세요.")