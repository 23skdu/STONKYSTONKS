# Stonky Stonks Tools

## Script Inventory & Descriptions

This repository contains several utility and analysis scripts:

*   **[stonky](file:///home/rsd/REPOS/STONKYSTONKS/stonky)**: An LSTM-based stock price prediction script using TensorFlow and Keras. It downloads historical data for a given ticker (e.g., `NVDA`), trains a sequential LSTM model, saves it as `.tfmodel.100`, and prints price predictions for future time horizons.
*   **[stats.py](file:///home/rsd/REPOS/STONKYSTONKS/stats.py)**: A command-line statistic calculator. It reads float data points from standard input (stdin) and prints descriptive statistics including Min/Max, Quartiles, Mean, Median, Harmonic Mean, Standard Deviation, Kurtosis, Skew, and Fibonacci levels (23.6%, 38.2%, 61.8%, 78.6%).
*   **[modeltest.py](file:///home/rsd/REPOS/STONKYSTONKS/modeltest.py)**: Evaluates several machine learning classification algorithms (Logistic Regression, Decision Tree, Random Forest, SVM) on a synthetically generated binary classification dataset, reporting cross-validated accuracy, precision, recall, and F1 metrics.
*   **[new_volprice_ema.py](file:///home/rsd/REPOS/STONKYSTONKS/new_volprice_ema.py)**: Calculates the price-to-volume ratio along with 25, 50, 100, and 200-day simple moving averages (SMAs) using `ta-lib` for a given ticker, displaying them on a matplotlib plot.
*   **[ytd_volprice.py](file:///home/rsd/REPOS/STONKYSTONKS/ytd_volprice.py)**: Downloads YTD stock data for a given ticker and plots the close price and volume side-by-side using twin y-axes.

## Running Unit Tests & Resolving Import Errors

If your IDE reports missing module errors (such as `Cannot find module 'yfinance'`, `numpy`, `matplotlib`, or `talib`), this is because dependencies need to be installed in a virtual environment.

### 1. Set Up a Virtual Environment
Create and activate a virtual environment, then install the required dependencies:
```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install the packages
pip install numpy pandas scipy scikit-learn yfinance matplotlib seaborn
```
*Note: `ta-lib` requires the system TA-Lib C-library headers to be installed. Alternatively, you can run inside Docker where all dependencies are preconfigured.*

### 2. Run the Unit Tests
Once the virtual environment is set up and active, run the test suite using:
```bash
python3 -m unittest discover -s tests
```
*All tests use mocked modules for external APIs like `yfinance` and dependencies like `talib` and `tensorflow`, allowing tests to run quickly offline.*




