from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import yfinance as yf
import warnings
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
import os

# TensorFlow 로그 레벨 설정 (INFO, WARNING 출력 억제)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# 경고 메시지 필터링
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

def create_dataset(dataset, time_step=60):
    X = []
    for i in range(len(dataset) - time_step):
        X.append(dataset[i:i + time_step, 0])
    return np.array(X)

# 삼성전자 (005930.KS)
ticker = '005930.KS'
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=4*365)).strftime('%Y-%m-%d')

# 데이터 로드 및 전처리
data = yf.download(ticker, start=start_date, end=end_date, progress=False)
data = data[['Close']].dropna()
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

# 데이터셋 생성
time_step = 60
X = create_dataset(scaled_data, time_step)
X = X.reshape(X.shape[0], X.shape[1], 1)

# 모델 로드
loaded_model = load_model("sam.h5")

# 예측 준비
last_60_days = scaled_data[-time_step:].reshape(1, time_step, 1)

# 예측 시 진행 상태 표시 끄기
predicted_price = loaded_model.predict(last_60_days, verbose=0)
sam_price = scaler.inverse_transform(predicted_price)[0][0]

# 예측값만 출력
print(f"{sam_price:.2f}")
