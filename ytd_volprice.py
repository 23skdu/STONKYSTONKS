#!/usr/bin/env python3
import argparse,os
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
parser = argparse.ArgumentParser()
parser.add_argument('ticker')
args=parser.parse_args()
data = yf.download(args.ticker, start='2024-01-01', end=None, rounding=False, progress=False)
fig, ax1 = plt.subplots()
color = 'tab:blue'
ax1.set_xlabel('Date')
ax1.set_ylabel('Close', color=color)
ax1.plot(data.index, data['Close'], color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Volume', color=color)
ax2.plot(data.index, data['Volume'], color=color)
ax2.tick_params(axis='y', labelcolor=color)
plt.show()
