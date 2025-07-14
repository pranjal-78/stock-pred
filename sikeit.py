from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}
    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        try:
            stock = yf.Ticker(ticker)
            end = datetime.now()
            start = end - timedelta(days=180)
            df = stock.history(start=start, end=end)

            if df.empty:
                result['error'] = "No data found. Please check the ticker symbol."
            else:
                df['Prev_Close'] = df['Close'].shift(1)
                df.dropna(inplace=True)

                X = df[['Prev_Close']]
                y = df['Close']

                model = LinearRegression()
                model.fit(X, y)

                latest_price = df['Close'].iloc[-1]
                predicted_price = model.predict(np.array([[latest_price]]))[0]
                percent_change = ((predicted_price - latest_price) / latest_price) * 100
                signal = "Buy ✅" if predicted_price > latest_price else "Sell ❌"
                investment = 10000
                estimated_return = investment * (percent_change / 100)

                result = {
                    'ticker': ticker,
                    'current_price': round(latest_price, 2),
                    'predicted_price': round(predicted_price, 2),
                    'trend': "↑ Upward" if percent_change > 0 else "↓ Downward",
                    'signal': signal,
                    'investment': investment,
                    'estimated_return': round(estimated_return, 2),
                    'percent_change': round(percent_change, 2)
                }

        except Exception as e:
            result['error'] = str(e)

    return render_template('./index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
