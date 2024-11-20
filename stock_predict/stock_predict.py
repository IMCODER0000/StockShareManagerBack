from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import yfinance as yf
import warnings
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

def create_dataset(dataset, time_step=60):
    X, y = [], []
    for i in range(len(dataset) - time_step):
        X.append(dataset[i:i + time_step, 0])
        y.append(dataset[i + time_step, 0])
    return np.array(X), np.array(y)

ticker = '005930.KS'

end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=4*365)).strftime('%Y-%m-%d')

data = yf.download(ticker, start=start_date, end=end_date)
data = data[['Close']]  # 종가만

data = data.dropna()

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)



time_step = 60
X, y = create_dataset(scaled_data, time_step)
X = X.reshape(X.shape[0], X.shape[1], 1)

train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]


# 모델 로드
loaded_model = load_model("sam.h5")

# 마지막 60일 데이터 준비
last_60_days = scaled_data[-time_step:]
last_60_days = last_60_days.reshape(1, -1)  # reshape to (1, 60) for single prediction
last_60_days = np.reshape(last_60_days, (1, time_step, 1))  # reshape to (1, 60, 1)

# 예측
predicted_price = loaded_model.predict(last_60_days)
predicted_price = scaler.inverse_transform(predicted_price)

sam_price = predicted_price[0][0]


# SK
ticker = '000660.KS'

end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=4*365)).strftime('%Y-%m-%d')

data = yf.download(ticker, start=start_date, end=end_date)
data = data[['Close']]  # 종가만

data = data.dropna()

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)



time_step = 60
X, y = create_dataset(scaled_data, time_step)
X = X.reshape(X.shape[0], X.shape[1], 1)

train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]


# 모델 로드
loaded_model = load_model("sk.h5")

# 마지막 60일 데이터 준비
last_60_days = scaled_data[-time_step:]
last_60_days = last_60_days.reshape(1, -1)  # reshape to (1, 60) for single prediction
last_60_days = np.reshape(last_60_days, (1, time_step, 1))  # reshape to (1, 60, 1)

# 예측
predicted_price = loaded_model.predict(last_60_days)
predicted_price = scaler.inverse_transform(predicted_price)

sk_price = predicted_price[0][0]


# LG
ticker = '373220.KS'

end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=4*365)).strftime('%Y-%m-%d')

data = yf.download(ticker, start=start_date, end=end_date)
data = data[['Close']]  # 종가만

data = data.dropna()

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)



time_step = 60
X, y = create_dataset(scaled_data, time_step)
X = X.reshape(X.shape[0], X.shape[1], 1)

train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]


# 모델 로드
loaded_model = load_model("lg.h5")

# 마지막 60일 데이터 준비
last_60_days = scaled_data[-time_step:]
last_60_days = last_60_days.reshape(1, -1)  # reshape to (1, 60) for single prediction
last_60_days = np.reshape(last_60_days, (1, time_step, 1))  # reshape to (1, 60, 1)

# 예측
predicted_price = loaded_model.predict(last_60_days)
predicted_price = scaler.inverse_transform(predicted_price)

lg_price = predicted_price[0][0]


# bio
ticker = '207940.KS'

end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=4*365)).strftime('%Y-%m-%d')

data = yf.download(ticker, start=start_date, end=end_date)
data = data[['Close']]  # 종가만

data = data.dropna()

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)



time_step = 60
X, y = create_dataset(scaled_data, time_step)
X = X.reshape(X.shape[0], X.shape[1], 1)

train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]


# 모델 로드
loaded_model = load_model("bio.h5")

# 마지막 60일 데이터 준비
last_60_days = scaled_data[-time_step:]
last_60_days = last_60_days.reshape(1, -1)  # reshape to (1, 60) for single prediction
last_60_days = np.reshape(last_60_days, (1, time_step, 1))  # reshape to (1, 60, 1)

# 예측
predicted_price = loaded_model.predict(last_60_days)
predicted_price = scaler.inverse_transform(predicted_price)

bio_price = predicted_price[0][0]


# hyundai
ticker = '005380.KS'

end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=4*365)).strftime('%Y-%m-%d')

data = yf.download(ticker, start=start_date, end=end_date)
data = data[['Close']]  # 종가만

data = data.dropna()

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)



time_step = 60
X, y = create_dataset(scaled_data, time_step)
X = X.reshape(X.shape[0], X.shape[1], 1)

train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]


# 모델 로드
loaded_model = load_model("hyun.h5")

# 마지막 60일 데이터 준비
last_60_days = scaled_data[-time_step:]
last_60_days = last_60_days.reshape(1, -1)  # reshape to (1, 60) for single prediction
last_60_days = np.reshape(last_60_days, (1, time_step, 1))  # reshape to (1, 60, 1)

# 예측
predicted_price = loaded_model.predict(last_60_days)
predicted_price = scaler.inverse_transform(predicted_price)

hyun_price = predicted_price[0][0]



print(sam_price)
print(sk_price)
print(lg_price)
print(bio_price)
print(hyun_price)