#!/usr/bin/env python3
import sys
import numpy as np
from scipy.stats import kurtosis, skew

# Read numbers from stdin
data = np.array([float(line.strip()) for line in sys.stdin])

# Compute statistics
min_val = np.min(data)
max_val = np.max(data)
median_val = np.median(data)
mean_val = np.mean(data)
std_dev = np.std(data)
kurtosis_val = kurtosis(data)
skew_val = skew(data)
avg_dev = np.mean(np.abs(data - mean_val))
sum_val = np.sum(data)
sum_squared = np.sum(data**2)
q1 = np.percentile(data, 25)
q3 = np.percentile(data, 75)
fib_23_6 = np.percentile(data, 23.6)
fib_38_2 = np.percentile(data, 38.2)
fib_61_8 = np.percentile(data, 61.8)
fib_78_6 = np.percentile(data, 78.6)

# Print results
print(f"Min: {min_val}")
print(f"Max: {max_val}")
print(f"Median: {median_val}")
print(f"Mean: {mean_val}")
print(f"Standard Deviation: {std_dev}")
print(f"Kurtosis: {kurtosis_val}")
print(f"Skew: {skew_val}")
print(f"Average Deviation: {avg_dev}")
print(f"Sum: {sum_val}")
print(f"Sum Squared: {sum_squared}")
print(f"1st Quartile: {q1}")
print(f"3rd Quartile: {q3}")
print(f"23.6% Fibonacci: {fib_23_6}")
print(f"38.2% Fibonacci: {fib_38_2}")
print(f"61.8% Fibonacci: {fib_61_8}")
print(f"78.6% Fibonacci: {fib_78_6}")
