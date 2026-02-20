import pandas as pd

# ファイルを読み込む（ファイル名は変えてください）
df = pd.read_csv('jsut_ver1.1.zip') 
# df = pd.read_excel('data.xlsx') # Excelの場合

# 1. 最初の5行を表示（どんなデータか見る）
print(df.head())

# 2. データのサイズ（行数, 列数）を確認
print(df.shape)

# 3. データの型や欠損値（null）がないか確認
print(df.info())

# 4. 統計量（平均や最大・最小）をサッと見る
print(df.describe())