import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
import warnings


warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)


ticker = input()


end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=4*365)).strftime('%Y-%m-%d')


data = yf.download(ticker, start=start_date, end=end_date)
data = data[['Close']]  # 종가만


data = data.dropna()


scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)


def create_dataset(dataset, time_step=60):
    X, y = [], []
    for i in range(len(dataset) - time_step):
        X.append(dataset[i:i + time_step, 0])
        y.append(dataset[i + time_step, 0])
    return np.array(X), np.array(y)

time_step = 60
X, y = create_dataset(scaled_data, time_step)
X = X.reshape(X.shape[0], X.shape[1], 1)


train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]


model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
model.add(Dropout(0.2))
model.add(LSTM(50))
model.add(Dropout(0.2))
model.add(Dense(25))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')


model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=0)


predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)
y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))


last_60_days = scaled_data[-time_step:]
last_60_days = last_60_days.reshape(1, -1)  # reshape to (1, 60) for single prediction
last_60_days = np.reshape(last_60_days, (1, time_step, 1))  # reshape to (1, 60, 1)


predicted_price = model.predict(last_60_days)
predicted_price = scaler.inverse_transform(predicted_price)  

print(f"{predicted_price[0][0]:.2f}")
