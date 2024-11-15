import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime
import sys

def analyze_portfolio(total_investment, risk_level, *selected_companies_names):
    # 입력값 검증
    if risk_level not in [3, 5, 7]:
        print("Risk level must be either 3, 5, or 7")
        return None
    
    if len(selected_companies_names) != 3:
        print("Exactly three company names are required")
        return None

    if total_investment <= 0:
        print("Total investment must be greater than 0")
        return None

    try:
        # KRX 상장 기업 정보 가져오기
        df_krx = fdr.StockListing('KRX')
        
        # 현재 날짜 설정
        current_date = datetime.now().strftime('%Y%m%d')
        start_date = pd.to_datetime(current_date) - pd.DateOffset(years=1)
        
        # 데이터프레임 초기화
        df_returns = pd.DataFrame()
        df_close_price = pd.DataFrame()
        
        # 각 종목에 대해 데이터 불러오기
        for company_name in selected_companies_names:
            try:
                company_code = df_krx[df_krx['Name'] == company_name]['Code'].values[0]
                print(f"Processing {company_name} ({company_code})")
                df_stock = fdr.DataReader(company_code, start_date, current_date)
                df_returns[company_name] = df_stock['Change']
                df_close_price[company_name] = df_stock['Close']
            except IndexError:
                print(f"Could not find company: {company_name}")
                return None
            except Exception as e:
                print(f"Error processing {company_name}: {str(e)}")
                return None
        
        return {
            'returns': df_returns.to_dict(),
            'prices': df_close_price.to_dict()
        }
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python stock_portfolio_analysis.py [total_investment] [risk_level] [stock1] [stock2] [stock3]")
        print("Example: python stock_portfolio_analysis.py 10000000 5 삼성전자 SK하이닉스 LG에너지솔루션")
        sys.exit(1)
    
    try:
        total_investment = float(sys.argv[1])
        risk_level = int(sys.argv[2])
        selected_companies = sys.argv[3:6]
        
        print(f"Starting analysis with:")
        print(f"Investment: {total_investment:,} KRW")
        print(f"Risk Level: {risk_level}")
        print(f"Companies: {', '.join(selected_companies)}")
        
        results = analyze_portfolio(total_investment, risk_level, *selected_companies)
        
        if results:
            print("Analysis completed successfully")
            print(results)
    except ValueError:
        print("Error: Total investment must be a number and risk level must be 3, 5, or 7")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
