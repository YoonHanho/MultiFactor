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


# 개별 복합 차트, 지수, 지수별 개별 라인 차트 
def multi_idx():

    # 차트 구성 지수 목록
    tickers = [
        ['다우지수', '^DJI'], ['나스닥', '^IXIC'], ['S&P500', '^GSPC'],
        ['니케이225', '^N225'], ['항셍', '^HSI'], ['유로스톡스', '^STOXX'],
        ['영국', '^FTSE'], ['독일', '^GDAXI'], ['비트코인', 'BTC/KRW'],
        ['코스피','KS11'], ['코스닥','KQ11'], ['코스피200','KS200'],
        ['상해','SSEC'], ['러셀','RUT'], ['VIX','VIX'],
        ['프랑스','FCHI'], ['WTI','CL=F'], ['브렌트유', 'BZ=F'],
        ['천연가스', 'NG=F'], ['금', 'GC=F'], ['은', 'SI=F'],
        ['구리','HG=F'], ['달러 원화','USD/KRW'], ['달러 유로화', 'USD/EUR'],
        ['달러 엔화','USD/JPY'], ['달러 위엔화', 'USD/CNY'],
        ['위엔화 원화', 'CNY/KRW'], ['10년 만기 미국국채', 'US10YT'],
        ['5년 만기 미국국채', 'US5YT'], ['30년 만기 미국국채', 'US30YT']
    ]

    ticker_dict = {item[0]: item[1] for item in tickers}
    index_options = ['없음'] + list(ticker_dict.keys())

    # 위젯 생성
    # 날짜 선택 위젯 (현재 기준 과거 3년치 자동 세팅)
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

    # 6개의 개별 콤보박스 위젯 생성
    default_values = ['다우지수', '나스닥', '코스피', '없음', '없음', '없음']
    comboboxes = []

    for i in range(6):
        cb = widgets.Combobox(
            value=default_values[i],
            placeholder='지수명 입력 (예: 나스닥)',
            options=index_options,
            description=f'지수 {i+1}:',
            ensure_option=True,
            disabled=False
        )
        comboboxes.append(cb)

    # 버튼 및 출력 영역 위젯
    button = widgets.Button(
        description="차트 생성", 
        button_style='info',
        icon='play'
    )
    output_area = widgets.Output()
    
    
    # 버튼 클릭 시 실행될 차트 생성 함수
    def generate_chart(b):
        with output_area:
            clear_output(wait=True)

            # 1) 입력된 조건 추출 (중복 및 '없음' 제거)
            selected_names = []
            for cb in comboboxes:
                if cb.value and cb.value != '없음' and cb.value in ticker_dict:
                    if cb.value not in selected_names:
                        selected_names.append(cb.value)
                        
            start_dt = start_date_picker.value.strftime('%Y-%m-%d')
            end_dt = end_date_picker.value.strftime('%Y-%m-%d')

            # 2) 선택된 지수 개수 검증
            n_selected = len(selected_names)
            if n_selected == 0:
                print("⚠️ 분석을 진행할 지수를 최소 1개 이상 선택해주세요.")
                return

            # 3) 동적 그리드 설정 (1~3개: 1줄, 4~6개: 2줄)
            rows = 1 if n_selected <= 3 else 2
            cols = 3

            fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows))
            axes_flat = axes.flatten() if rows == 2 else axes

            print(f"데이터를 불러오는 중입니다... ({start_dt} ~ {end_dt})")

            # 4) 데이터 다운로드 및 차트 그리기
            for i in range(rows * cols):
                if i < n_selected:
                    name = selected_names[i]
                    ticker = ticker_dict[name]
                    try:
                        # 데이터 수집
                        df = fdr.DataReader(ticker, start_dt, end_dt)['Close']

                        # 시계열 차트 생성
                        df.plot(kind='line', ax=axes_flat[i], color='tab:blue', linewidth=1.5)
                        axes_flat[i].set_title(name, fontsize=12, fontweight='bold')
                        axes_flat[i].grid(True, axis='y', linestyle='--', alpha=0.5)
                        axes_flat[i].set_xlabel('')
                        axes_flat[i].set_ylabel('')
                    except Exception as e:
                        axes_flat[i].set_title(f"{name} (데이터 로드 실패)")
                        axes_flat[i].text(0.5, 0.5, "Data Not Found", ha='center', va='center')
                else:
                    # 사용하지 않는 빈 축 숨기기
                    axes_flat[i].axis('off')

            plt.tight_layout()
            plt.show()

    # 버튼 이벤트 연결
    button.on_click(generate_chart)

    # 5. 화면에 위젯 UI 출력 (주식 스크리너와 동일한 레이아웃 적용)
    ui_top = widgets.HBox([start_date_picker, end_date_picker, button])
    ui_mid = widgets.HBox(comboboxes[:3])
    ui_bot = widgets.HBox(comboboxes[3:])

    display(widgets.VBox([ui_top, ui_mid, ui_bot, output_area]))

    # 초기 자동 실행 (원치 않으시면 주석 처리)
    generate_chart(None)	