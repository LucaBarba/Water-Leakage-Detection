import pandas as pd

# List of input files
input_files = [
    "L-Town_data/4017659/2018_Leakages.csv",
    "L-Town_data/4017659/2019_Leakages.csv"
]

for file in input_files:
    df = pd.read_csv(file, sep=";", decimal=",")
    output_file = file.replace(".csv", "_clean.csv")
    df.to_csv(output_file, sep=";", index=False)
