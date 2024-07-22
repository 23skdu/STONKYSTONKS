#!/usr/bin/env python3
import sys
import yfinance as yf
import pandas as pd
import talib
import matplotlib.pyplot as plt

def main(ticker):
    # Fetch historical data
    data = yf.download(ticker, period="1y")
    
    # Calculate price over volume
    data['Price/Volume'] = data['Close'] / data['Volume']
    
    # Calculate moving averages
    data['MA25'] = talib.SMA(data['Close'], timeperiod=25)
    data['MA50'] = talib.SMA(data['Close'], timeperiod=50)
    data['MA100'] = talib.SMA(data['Close'], timeperiod=100)
    data['MA200'] = talib.SMA(data['Close'], timeperiod=200)
    
    # Plotting
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['Price/Volume'], label='Price/Volume', color='blue')
    plt.plot(data.index, data['MA25'], label='25-day MA', color='red')
    plt.plot(data.index, data['MA50'], label='50-day MA', color='green')
    plt.plot(data.index, data['MA100'], label='100-day MA', color='orange')
    plt.plot(data.index, data['MA200'], label='200-day MA', color='purple')
    
    plt.title(f'Price/Volume and Moving Averages for {ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price/Volume')
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <ticker>")
    else:
        ticker = sys.argv[1]
        main(ticker)

