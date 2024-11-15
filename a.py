import pandas as pd
from datetime import datetime
import numpy as np
import sys
import FinanceDataReader as fdr
import itertools
from pykrx import bond

# sys.argv를 사용하여 종목 이름들을 리스트로 받음
selected_companies_names = sys.argv[1:4]

# KRX 상장 주식 목록 가져오기
df_krx = fdr.StockListing('KRX')

# 현재 날짜 사용
current_date = datetime.now().strftime('%Y%m%d')
start_date = pd.to_datetime(current_date) - pd.DateOffset(years=1)

# 종목 이름을 종목 코드로 변환하고 등락률을 저장할 데이터프레임 초기화
df_returns = pd.DataFrame()
df_close_price = pd.DataFrame()

# 각 종목에 대해 데이터 불러오고 등락률 가져오기
for company_name in selected_companies_names:
    try:
        # 종목 코드 가져오기
        company_code = df_krx[df_krx['Name'] == company_name]['Code'].values[0]
        df_stock = fdr.DataReader(company_code, start_date, current_date)
        df_returns[company_name] = df_stock['Change']
        df_close_price[company_name] = df_stock['Close']
    except IndexError:
        pass

# 일일 평균 수익률 및 변동성 계산
daily_stock_average_d = []
average_returns = df_returns.mean()
average_returns = average_returns * len(df_returns)
for value in average_returns:
    daily_stock_average_d.append(value)

personal_stock_v = []
std_dev = df_returns.std()
total_days = len(df_returns)
volatility = std_dev * (total_days ** 0.5)
for value in volatility:
    personal_stock_v.append(value)

# 상관계수 계산
p12_correlation = df_close_price[selected_companies_names[0]].corr(df_close_price[selected_companies_names[1]])
p13_correlation = df_close_price[selected_companies_names[0]].corr(df_close_price[selected_companies_names[2]])
p23_correlation = df_close_price[selected_companies_names[1]].corr(df_close_price[selected_companies_names[2]])
stock_corr = [p12_correlation, p13_correlation, p23_correlation]

# 가능한 조합 찾기
def find_combinations():
    possible_values = [i / 100 for i in range(101)]  # 0부터 1까지 0.01 간격으로 조합 추출
    combinations = itertools.product(possible_values, repeat=3)

    valid_combinations = []
    valid_indices = []

    for i, combo in enumerate(combinations):
        if round(sum(combo), 2) == 1.0 and all(0.1 <= x <= 0.7 for x in combo):  # 최대 0.7, 최소 0.1은 가지는 조합만 추출
            valid_combinations.append(combo)
            valid_indices.append(i)

    return valid_combinations, valid_indices

result, valid_indices = find_combinations()

# 포트폴리오 수익률 계산
port_returns = []
for combo in result:
    port_return = sum(x * er for x, er in zip(combo, daily_stock_average_d))
    port_returns.append(port_return)

# 국채 3년 수익률 가져오기
date = current_date
df = bond.get_otc_treasury_yields(date)
kukko_3year_yield = df.loc['국고채 3년', '수익률'] / 100
formatted_yield = f"{kukko_3year_yield:.3f}"  # 소수점 셋째 자리까지 출력

# 포트폴리오 변동성 계산
port_vol = []
for combo in result:
    term1 = sum(x ** 2 * sigma ** 2 for x, sigma in zip(combo, personal_stock_v))
    term2 = 0

    for i in range(len(combo) - 1):
        for j in range(i + 1, len(combo)):
            idx = i * (len(combo) - 1) + j - 1
            corr_idx = min(idx, 2)
            term2 += 2 * combo[i] * combo[j] * personal_stock_v[i] * personal_stock_v[j] * stock_corr[corr_idx]

    port_volatility = (term1 + term2) ** 0.5
    port_vol.append(port_volatility)

# 정부 국채 수익률 (Rf) 설정
Rf = float(formatted_yield)

# 샤프 비율 계산
Cal_values = []
for i in range(len(port_returns)):
    Cal = (port_returns[i] - Rf) / port_vol[i]
    Cal_values.append(Cal)

# 가장 높은 샤프 비율을 가지는 조합 찾기
max_cal_value = max(Cal_values)
max_cal_index = Cal_values.index(max_cal_value)
max_result = result[max_cal_index]

# 총 투자 금액 및 위험도 입력 받기
Investment = int(sys.argv[4])
danger = int(sys.argv[5])  # 고위험 = 7, 중위험 = 5, 저위험 = 3

# 투자 금액 분배 계산
invest_amount = []
real_invest = (Investment * (danger * 0.1))
rf = Investment - real_invest
for i in range(len(max_result)):
    price = real_invest * max_result[i]
    invest_amount.append(price)

# 결과 출력
print("총 투자 금액 : {:,.0f}".format(Investment))
print("rf : {:,.0f}".format(rf))
for i in range(len(selected_companies_names)):
    print("{} 투자 금액: {:,.0f}".format(selected_companies_names[i], invest_amount[i]))
