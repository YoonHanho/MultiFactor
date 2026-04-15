# MultiFactor 📈

**MultiFactor**는 국내상장주식(코스피/코스닥)을 대상으로 멀티팩터(Multi-Factor) 전략을 손쉽게 적용하고, 팩터별 점수 및 종합 순위를 산출해 주는 파이썬 패키지입니다. 
종목별 주가와 재무 데이터 수집은 `FinanceDataReader`를 기반으로 구동됩니다. 

<br>

## 📌 멀티팩터 전략이란?
주식 투자에서 멀티팩터(Multi-Factor) 기법은 주가의 수익률에 영향을 미치는 여러 가지 핵심 요인(팩터)을 동시에 고려하여 종목을 고르고 포트폴리오를 운용하는 데이터에 기반한 정량적 투자 전략입니다. 

단순히 '저평가된 주식'만 찾거나 '상승 추세인 주식'만 사는 것이 아니라, 다양한 성공 요소를 결합하여 단일 팩터의 약점을 보완하고 보다 안정적인 초과 수익을 추구합니다. MultiFactor 라이브러리는 다음 3가지 핵심 팩터의 점수를 계산하고 이를 종합점수로 환산한 후 순위화한 결과를 제공합니다.

| 팩터 (Factor) | 핵심 개념 | 주요 지표 |
| :--- | :--- | :--- |
| **모멘텀 (Momentum)** | 과거에 우수한 성과를 보인 주식이 미래에도 상승 추세를 이어갈 것이라는 가정 | 주가 상승률, 거래량 |
| **밸류 (Value)** | 기업의 내재 가치 대비 저평가된 주식을 발굴 | PER, PBR |
| **퀄리티 (Quality)** | 우량한 펀더멘털, 안정적인 수익성, 장기 성장 잠재력을 갖춘 기업에 집중 | 매출성장률, 영업이익성장률, ROE |

<br>

## ✨ 주요 기능
* **국내 주식 멀티팩터 데이터 제공:** 가치, 모멘텀, 퀄리티 지표 및 이를 합산한 종합 점수 산출

| 구분 | 주요 기능 | 함수명 |
| -------- | -------- | -------- |
| 종목 정보 수집     | 시가총액 기준 상위 종목들의 기본 정보(종목코드, 종목명, 시가총액, 업종, 최근 종가 등)를 수집합니다. | get_stockinfo()  |
| 멀티팩터 종합점수    | 종목별 멀티팩터 세부 지표 점수와 종합 점수, 그리고 전체 순위를 산출합니다. | get_score()  |
| 투자스타일별 종합점수    | 3가지 투자 스타일(안정추구, 추세성장, 역발상 등)에 맞춰 가중치가 조정된 멀티팩터 종합 점수를 제공합니다. | get_score_adj_weight()  |
| 종합점수 그룹화    | 산출된 종합 점수를 바탕으로 전체 종목을 N개의 그룹으로 분류하고, 그룹별 종목명을 출력합니다.| get_Ngroup()  |
| 특정 종목 팩터 조회  | 단일 종목에 대한 개별 팩터(모멘텀, 밸류, 퀄리티) 값을 빠르게 조회합니다. | get_momentum_one() <br> get_value_one() <br>  get_quality_one()  |


* **투자 유형별 가중치 조절한 멀티팩터 데이터 제공 :** 투자 스타일에 맞춘 3가지 모델 제공
  * **가치성장:** 밸류 + 퀄리티 조합 ("기업의 본질적인 가치와 안정성을 중요하게 생각하며, 장기적인 관점에서 투자")
  * **추세성장:** 모멘텀 + 밸류 조합 ("시장의 흐름과 성장을 중요하게 생각하고, 주가 상승에 적극적으로 참여")
  * **역발상:** 밸류 + 모멘텀 조합 ("저평가 종목이 다시 반등하는 시점을 찾아 투자 기회를 포착")

<br>


## ⚙️ 설치 방법 (Installation)
 다음 코드를 실행하여 각자의 PC(또는 실습 환경)에 MultiFactor 라이브러리를 설치합니다. 이 과정은 최초 1회만 수행하면 됩니다.
```python
!pip install MultiFactor
```

만약 기존에 설치된 라이브러리를 최신 버전으로 업데이트해야 한다면 아래의 코드를 실행합니다.
```python
!pip install --upgrade MultiFactor
```

<br>

## 🚀 빠른 시작 (Quick Start)

### 1. 패키지 불러오기 
다음 코드로 멀티팩터 패키지를 불러옵니다. 
```python
from MultiFactor import MultiFactor
```

<br>

### 2. 멀티팩터 객체 생성  
멀티팩터 객체 생성 시, 수집 대상 종목 수(N)를 반드시 지정해야 합니다. N은 시가총액 상위 순으로 N개까지 종목을 수집함을 의미합니다. N이 커질수록 데이터 수집 시간이 길어지므로, 초기 테스트에는 종목수(N)를 5~50 사이로 지정한 후 차츰 늘려가기를 권장합니다. 
```python
mf = MultiFactor(N=50)  # 시가총액 상위 50개 종목 
```
<br>

### 3. 종목 정보 수집 
멀티팩터 객체에서 지정한 종목수(N) 만큼 종목 정보 데이터를 생성합니다. 반환되는 데이터 형식은 데이터프레임(기본값) 또는 딕셔너리로 지정할 수 있습니다. 

```python
# 종목 코드 정보 생성 (데이터프레임)
df = mf.get_stockinfo() 

# 종목코드, 종목명, 시가총액 출력 (최초 5건) 
df[['Code', 'Name', 'Marcap']].head()   
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Code</th>
      <th>Name</th>
      <th>Marcap</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>005930</td>
      <td>삼성전자</td>
      <td>1147817793075800</td>
    </tr>
    <tr>
      <th>1</th>
      <td>000660</td>
      <td>SK하이닉스</td>
      <td>691321294050000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>005380</td>
      <td>현대차</td>
      <td>106883553852000</td>
    </tr>
    <tr>
      <th>3</th>
      <td>373220</td>
      <td>LG에너지솔루션</td>
      <td>89037000000000</td>
    </tr>
    <tr>
      <th>4</th>
      <td>402340</td>
      <td>SK스퀘어</td>
      <td>77535136505000</td>
    </tr>
  </tbody>
</table>


```python
# 종목 코드 정보 생성 (딕셔너리) 
stock_list = mf.get_stockinfo(dtype='dic')  # {'종목코드': '종목명'}
print(stock_list)

# {'005930': '삼성전자', '000660': 'SK하이닉스', '005380': '현대차', ... }
``` 

<br>


### 4.멀티팩터 종합 점수 데이터 수집
```get_score```함수로 멀티팩터 종합점수 데이터를 간단하게 생성할 수 있습니다. 다음 코드는 시가총액 상위 10개 종목의 종합 점수를 추출하여 파이썬 데이터프레임(df)에 저장합니다.

```python 
from MultiFactor import MultiFactor
mf = MultiFactor(N=10) 
df = mf.get_score()
```

이 데이터프레임 안에는 분석에 필요한 총 23개의 컬럼(열)이 담겨 있습니다. 컬럼은 크게 4개 유형을 구분할 수 있습니다. 

- 종목정보 : 종목코드, 종목명
- 종합지표 원본 : 모멘텀 주가, 모멘텀 거래량, PER, PBR, 매출 증가율, 영업이익 증가율, 순이익 증가율, ROE 
- 종합지표 순위 :종합 지표 원본 데이터를 추출된 N개 종목 내에서의 상대 순위로 환산한 값
- 종합점수/순위 : 종합 지표 순위들의 평균값 및 이를 바탕으로 매긴 최종 순위


<b>① 종합지표 원본 추출 예시</b>

종합지표 원본 데이터를 출력하여 결과를 해석합니다. 

```python
cols = ['scode', 'sname', 'mom_price', 'mom_vol', 'PER', 'PBR', 
        'revenue_rate', 'oper_income_rate', 'net_income_rate', 'ROE']
df[cols].head()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>scode</th>
      <th>sname</th>
      <th>mom_price</th>
      <th>mom_vol</th>
      <th>PER</th>
      <th>PBR</th>
      <th>revenue_rate</th>
      <th>oper_income_rate</th>
      <th>net_income_rate</th>
      <th>ROE</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>402340</td>
      <td>SK스퀘어</td>
      <td>105.54</td>
      <td>2.99</td>
      <td>5.54</td>
      <td>1.73</td>
      <td>9.76</td>
      <td>17.12</td>
      <td>32.01</td>
      <td>37.08</td>
    </tr>
    <tr>
      <th>1</th>
      <td>000660</td>
      <td>SK하이닉스</td>
      <td>80.87</td>
      <td>-9.40</td>
      <td>11.03</td>
      <td>3.73</td>
      <td>34.27</td>
      <td>68.40</td>
      <td>21.02</td>
      <td>44.14</td>
    </tr>
    <tr>
      <th>2</th>
      <td>005930</td>
      <td>삼성전자</td>
      <td>47.69</td>
      <td>-17.79</td>
      <td>17.89</td>
      <td>1.82</td>
      <td>9.04</td>
      <td>65.00</td>
      <td>60.66</td>
      <td>10.78</td>
    </tr>
    <tr>
      <th>3</th>
      <td>000270</td>
      <td>기아</td>
      <td>14.42</td>
      <td>-32.69</td>
      <td>6.38</td>
      <td>0.77</td>
      <td>-2.09</td>
      <td>26.00</td>
      <td>3.40</td>
      <td>12.91</td>
    </tr>
    <tr>
      <th>4</th>
      <td>105560</td>
      <td>KB금융</td>
      <td>22.34</td>
      <td>-17.47</td>
      <td>6.59</td>
      <td>0.52</td>
      <td>-37.96</td>
      <td>9.47</td>
      <td>-5.29</td>
      <td>9.50</td>
    </tr>
  </tbody>
</table>


 
<b>② 종합지표 순위 추출 예시</b>

```python
cols = ['scode', 'sname', '모멘텀_주가', '모멘텀_거래량', '밸류_PER', '밸류_PBR', 
        '퀄리티_ROE', '퀄리티_매출증가', '퀄리티_영업이익증가', '퀄리티_순이익증가']
df[cols].head()
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>scode</th>
      <th>sname</th>
      <th>모멘텀_주가</th>
      <th>모멘텀_거래량</th>
      <th>밸류_PER</th>
      <th>밸류_PBR</th>
      <th>퀄리티_ROE</th>
      <th>퀄리티_매출증가</th>
      <th>퀄리티_영업이익증가</th>
      <th>퀄리티_순이익증가</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>402340</td>
      <td>SK스퀘어</td>
      <td>10</td>
      <td>10</td>
      <td>10</td>
      <td>40</td>
      <td>20</td>
      <td>40</td>
      <td>50</td>
      <td>30</td>
    </tr>
    <tr>
      <th>1</th>
      <td>000660</td>
      <td>SK하이닉스</td>
      <td>20</td>
      <td>30</td>
      <td>50</td>
      <td>80</td>
      <td>10</td>
      <td>10</td>
      <td>10</td>
      <td>40</td>
    </tr>
    <tr>
      <th>2</th>
      <td>005930</td>
      <td>삼성전자</td>
      <td>40</td>
      <td>50</td>
      <td>60</td>
      <td>50</td>
      <td>60</td>
      <td>50</td>
      <td>20</td>
      <td>10</td>
    </tr>
    <tr>
      <th>3</th>
      <td>000270</td>
      <td>기아</td>
      <td>80</td>
      <td>60</td>
      <td>20</td>
      <td>30</td>
      <td>50</td>
      <td>80</td>
      <td>40</td>
      <td>50</td>
    </tr>
    <tr>
      <th>4</th>
      <td>105560</td>
      <td>KB금융</td>
      <td>70</td>
      <td>40</td>
      <td>30</td>
      <td>10</td>
      <td>70</td>
      <td>90</td>
      <td>60</td>
      <td>60</td>
    </tr>
  </tbody>
</table>



<b>③ 종합점수/순위 추출 예시</b>

```python
cols = ['scode', 'sname', '종합점수', '종합순위', '종합순위_퍼센트']
df[cols].head()
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>scode</th>
      <th>sname</th>
      <th>종합점수</th>
      <th>종합순위</th>
      <th>종합순위_퍼센트</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>402340</td>
      <td>SK스퀘어</td>
      <td>26</td>
      <td>1</td>
      <td>10</td>
    </tr>
    <tr>
      <th>1</th>
      <td>000660</td>
      <td>SK하이닉스</td>
      <td>31</td>
      <td>2</td>
      <td>20</td>
    </tr>
    <tr>
      <th>2</th>
      <td>005930</td>
      <td>삼성전자</td>
      <td>42</td>
      <td>3</td>
      <td>30</td>
    </tr>
    <tr>
      <th>3</th>
      <td>000270</td>
      <td>기아</td>
      <td>51</td>
      <td>4</td>
      <td>40</td>
    </tr>
    <tr>
      <th>4</th>
      <td>105560</td>
      <td>KB금융</td>
      <td>54</td>
      <td>5</td>
      <td>50</td>
    </tr>
  </tbody>
</table>


<br>

### 5. 투자 스타일별 종합점수 출력 

3가지로 분류된 투자 유형별로 멀티팩터 종합 점수 데이터를 생성할 수 있습니다. 

```python
# 시가총액 상위 100 종목 멀티팩터 종합점수 추출 
mf = MultiFactor(N=100)  
df = mf.get_score()  
``` 


① 가치 성장 전략 : 밸류 + 퀄리티 조합

```python
df = mf.get_score_adj_weight(df, weight='가치성장') 
df[['scode', 'sname', '종합점수', '종합순위']].head()  
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>scode</th>
      <th>sname</th>
      <th>종합점수</th>
      <th>종합순위</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>028050</td>
      <td>삼성E&amp;A</td>
      <td>24</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>267250</td>
      <td>HD현대</td>
      <td>24</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>064400</td>
      <td>LG씨엔에스</td>
      <td>25</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>000660</td>
      <td>SK하이닉스</td>
      <td>26</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>402340</td>
      <td>SK스퀘어</td>
      <td>27</td>
      <td>5</td>
    </tr>
  </tbody>
</table>


② 추세 성장 전략 : 모멘텀 + 퀄리티 조합

```python
df = mf.get_score_adj_weight(df, weight='추세성장') 
df[['scode', 'sname', '종합점수', '종합순위']].head()   
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>scode</th>
      <th>sname</th>
      <th>종합점수</th>
      <th>종합순위</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>278470</td>
      <td>에이피알</td>
      <td>12</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>000660</td>
      <td>SK하이닉스</td>
      <td>14</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>402340</td>
      <td>SK스퀘어</td>
      <td>18</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>010120</td>
      <td>LS ELECTRIC</td>
      <td>20</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>028050</td>
      <td>삼성E&amp;A</td>
      <td>22</td>
      <td>5</td>
    </tr>
  </tbody>
</table>


③ 역발상 전략 : 밸류 + 모멘텀 조합

```python
df = mf.get_score_adj_weight(df, weight='역발상') 
df[['scode', 'sname', '종합점수', '종합순위']].head()   
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>scode</th>
      <th>sname</th>
      <th>종합점수</th>
      <th>종합순위</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>000880</td>
      <td>한화</td>
      <td>16</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>039490</td>
      <td>키움증권</td>
      <td>19</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>006800</td>
      <td>미래에셋증권</td>
      <td>19</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>047040</td>
      <td>대우건설</td>
      <td>20</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>071050</td>
      <td>한국금융지주</td>
      <td>22</td>
      <td>6</td>
    </tr>
  </tbody>
</table>

<br>

### 6. 종합점수별 그룹화 출력
get_Ngroup() 함수를 사용하면 전체 종목을 원하는 개수의 그룹으로 깔끔하게 묶어 요약할 수 있습니다.

```python
mf = MultiFactor(N=100)
df = mf.get_score()  
mf.get_Ngroup(df, Ngroup=10)  # 종합점수 상위 순 10개 그룹으로 분류

# [출력 결과]
# 1 : SK스퀘어, SK하이닉스, 삼성E&A, HD현대, 에이피알, 한국금융지주, 삼성전자, LG이노텍, 키움증권, LS ELECTRIC
# 2 : 효성중공업, NH투자증권, 이수페타시스, 삼성물산, 삼성증권, HD현대일렉트릭, LG씨엔에스, LS, HD한국조선해양, 현대건설
# 3 : 코오롱티슈진, 한화, 고려아연, 하나금융지주, JB금융지주, 미래에셋증권, KB금융, 삼천당제약, 기업은행, 엘앤에프
# 4 : DB손해보험, 기아, 한전기술, 셀트리온, 우리금융지주, 펩트론, BNK금융지주, 대우건설, 한국항공우주, 현대글로비스
# 5 : 삼성생명, 신한지주, HD현대중공업, 한화에어로스페이스, 현대모비스, 한화솔루션, 현대차, 삼양식품, 삼성카드, 에이비엘바이오
# 6 : SK바이오팜, LG유플러스, 한미약품, S-Oil, GS, KT, 한화오션, 삼성화재, 두산, 삼성전기
# 7 : SK텔레콤, 카카오뱅크, 한국전력, 한국타이어앤테크놀로지, HMM, 삼성중공업, 포스코인터내셔널, SK, 현대로템, 카카오페이
# 8 : 대한항공, 현대오토에버, CJ, LIG넥스원, 삼성SDI, HD건설기계, HD현대마린솔루션, 두산에너빌리티, 크래프톤, 하이브
# 9 : HLB, 삼성에스디에스, KT&G, 아모레퍼시픽, 유한양행, 한화시스템, SK이노베이션, LG전자, 삼성에피스홀딩스, NAVER
# 10 : LG, 레인보우로보틱스, 한미반도체, POSCO홀딩스, LG에너지솔루션, 카카오, LG화학, 삼성바이오로직스, 한진칼, 포스코퓨처엠
```

<br>

### 7. 개별 지표 데이터 수집
특정 팩터의 데이터만 개별적으로 추출할 수 있습니다.

```python
# 개별 팩터 데이터 추출 (인자로 stock_list 딕셔너리 주입)
data_mom = mf.get_momentum(stock_list)
data_val = mf.get_value(stock_list)
data_fin = mf.get_quality(stock_list)

# 추출한 개별 팩터 데이터를 조합하여, 종합 점수 산정
data_mast_custom = mf.get_score_by_data(data_mom, data_val, data_fin)
```

<br>


### 8. 특정 종목 팩터 값 조회
개별 종목(예: 삼성전자 '005930')의 팩터 점수만 빠르게 확인하고 싶을 때 활용합니다.

```python
# 삼성전자의 모멘텀 데이터
mf.get_momentum_one('005930')
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>scode</th>
      <th>mom_price</th>
      <th>mom_vol</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>005930</td>
      <td>62.531321</td>
      <td>-40.739685</td>
    </tr>
  </tbody>
</table>

```python
# 삼성전자의 밸류 데이터
mf.get_value_one('005930')
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>scode</th>
      <th>PER</th>
      <th>PBR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>005930</td>
      <td>17.89</td>
      <td>1.82</td>
    </tr>
  </tbody>
</table>

```python
# 삼성전자의 퀄리티 데이터
mf.get_quality_one('005930') 
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>scode</th>
      <th>revenue_rate</th>
      <th>oper_income_rate</th>
      <th>net_income_rate</th>
      <th>ROE</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>005930</td>
      <td>9.03503</td>
      <td>64.997</td>
      <td>60.659103</td>
      <td>10.78</td>
    </tr>
  </tbody>
</table>

<br>

## 🌎 미국 주식 분석 (US Stocks) 🇺🇸

**MultiFactorUS** 클래스를 사용하면 미국 주식(S&P 500, NASDAQ, NYSE 등)에 대해서도 국내 주식과 동일한 인터페이스로 멀티팩터 분석을 수행할 수 있습니다. 미국 주식 분석은 `yfinance` 라이브러리를 기반으로 구동됩니다.

### 1. 미국 주식 분석 시작하기
```python
from MultiFactor import MultiFactorUS

# 미국 시가총액 상위 100개 종목 분석 객체 생성 (기본값 500)
mf_us = MultiFactorUS(N=100)

# 멀티팩터 종합 점수 및 순위 계산
df_us = mf_us.get_score()
```

### 2. 주요 특징
* **실시간 데이터**: `yfinance`를 활용하여 미국 시장의 최신 주가 및 재무 지표를 수집합니다.
* **티커 호환성**: `BRK-B`와 같이 슬래시나 마침표가 포함된 특수 티커들을 내부적으로 자동 변환하여 데이터 수집 오류를 최소화합니다.
* **동일한 환경**: 국내 주식과 동일한 함수명(`get_score`, `get_Ngroup` 등)을 사용하므로 기존 코드를 쉽게 재사용할 수 있습니다.

### 3. 스타일별 가중치 및 그룹화 활용
```python
# '추세성장' 스타일 가중치 적용
df_adj = mf_us.get_score_adj_weight(df_us, weight='추세성장')

# 종합 순위에 따라 10개 그룹으로 분류 및 종목 출력
mf_us.get_Ngroup(df_adj, Ngroup=10)
```

<br>

## ⚠️ 투자자 유의사항 (Disclaimer)

> **MultiFactor** 라이브러리에서 제공하는 모든 데이터와 분석 결과(종합 점수, 순위 등)는 투자 참고용일 뿐이며, 그 정확성이나 완전성을 보장하지 않습니다. 
> 
> * 본 라이브러리는 종목 추천을 목적으로 하지 않으며, 과거의 데이터나 높은 팩터 점수가 미래의 수익을 보장하지 않습니다.
> * 데이터 수집 과정에서 지연, 누락, 오류가 발생할 수 있습니다.
> * 본 라이브러리의 결과물을 활용한 투자 결정으로 인해 발생하는 어떠한 직·간접적인 손실에 대해서도 개발자(저자)는 일체의 법적 책임을 지지 않습니다.
> * **최종 투자 판단과 그에 따른 책임은 전적으로 투자자 본인에게 있습니다.**