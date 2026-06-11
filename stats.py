#!/usr/bin/env python3
import sys
import numpy as np
from scipy.stats import kurtosis, skew
def calculate_stats(data):
    data = np.array(data)
    min_val = np.min(data)
    fib_23_6 = np.percentile(data, 23.6)
    q1 = np.percentile(data, 25)
    fib_38_2 = np.percentile(data, 38.2)
    median_val = np.median(data)
    mean_val = np.mean(data)
    harmonic_mean_val = data / np.sum(1.0/data)
    fib_61_8 = np.percentile(data, 61.8)
    q3 = np.percentile(data, 75)
    fib_78_6 = np.percentile(data, 78.6)
    max_val = np.max(data)
    std_dev = np.std(data)
    kurtosis_val = kurtosis(data)
    skew_val = skew(data)
    avg_dev = np.mean(np.abs(data - mean_val))
    return {
        "Min": min_val,
        "23.6% Fibonacci": fib_23_6,
        "1st Quartile": q1,
        "38.2% Fibonacci": fib_38_2,
        "Median": median_val,
        "Mean": mean_val,
        "HarmonicMean": harmonic_mean_val,
        "61.8% Fibonacci": fib_61_8,
        "3rd Quartile": q3,
        "78.6% Fibonacci": fib_78_6,
        "Max": max_val,
        "Standard Deviation": std_dev,
        "Kurtosis": kurtosis_val,
        "Skew": skew_val,
        "Average Deviation": avg_dev
    }

if __name__ == "__main__":
    input_data = np.array([float(line.strip()) for line in sys.stdin])
    res = calculate_stats(input_data)
    for key, val in res.items():
        print(f"{key}: {val}")

