import os
import numpy as np
import librosa

# ==========================================
# 設定（あなたの環境に合わせて書き換えてください）
# ==========================================
DATASET_PATH = "../dataset"  # データが入っている一番上のフォルダパス
TARGET_WIDTH = 32           # 横幅（時間の長さ）をここに統一する
SR = 16000                  # サンプリングレート
N_MELS = 128                # メルスペクトログラムの高さ

# ==========================================
# 関数定義
# ==========================================

def normalize_audio(y):
    """ 音量を正規化する（あなたのコード） """
    max_val = np.max(np.abs(y))
    if max_val == 0:
        return y
    return y / max_val

def adjust_width(spectrogram, target_width):
    """ 
    スペクトログラムの横幅を target_width に強制統一する 
    (短いなら0埋め、長いならカット)
    """
    current_width = spectrogram.shape[1]
    
    if current_width < target_width:
        # 足りない部分を0埋め (padding)
        pad_width = target_width - current_width
        # ((縦はそのまま), (横の右側に0を足す))
        return np.pad(spectrogram, ((0, 0), (0, pad_width)), mode='constant')
    else:
        # 長すぎる場合はカット (trim)
        return spectrogram[:, :target_width]

# ==========================================
# メイン処理：データの読み込み
# ==========================================
print("データを読み込んでいます...")

X_list = []  # データを一時的に入れるリスト
y_list = []  # ラベルを入れるリスト

# フォルダ一覧を取得（これがクラス名になります）
# 例: classes = ['cat', 'dog', 'tree'...]
classes = sorted([d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))])
print(f"検出されたクラス数: {len(classes)}")
print(f"クラス一覧: {classes}")

# クラス名と数字の対応表を作る (例: {'cat': 0, 'dog': 1})
label_map = {label: i for i, label in enumerate(classes)}

total_files = 0

for label_name in classes:
    class_dir = os.path.join(DATASET_PATH, label_name)
    label_id = label_map[label_name]  # 正解ラベルの数字 (0~34)
    
    # フォルダ内のファイルを走査
    with os.scandir(class_dir) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith(('.wav', '.mp3')):
                try:
                    # 1. ロード
                    y, _ = librosa.load(entry.path, sr=SR)
                    
                    # 2. 正規化
                    y_norm = normalize_audio(y)
                    
                    # 3. メルスペクトログラム変換
                    S = librosa.feature.melspectrogram(y=y_norm, sr=SR, n_mels=N_MELS, fmax=8000)
                    
                    # 4. dB変換
                    S_dB = librosa.power_to_db(S, ref=np.max)
                    
                    # 5. 【重要】サイズを (128, 32) に統一
                    S_fixed = adjust_width(S_dB, TARGET_WIDTH)
                    
                    # リストに追加
                    X_list.append(S_fixed)
                    y_list.append(label_id)
                    total_files += 1
                    
                    if total_files % 100 == 0:
                        print(f"{total_files} ファイル処理完了...")

                except Exception as e:
                    print(f"エラースキップ: {entry.name} - {e}")

# ==========================================
# Numpy配列に変換（ここが CNN への入力になる）
# ==========================================

# リストを numpy 配列にする
X_data = np.array(X_list)
y_label = np.array(y_list)

# CNN用に形を整える
# 現在の形: (データ数, 128, 32)
# 目標の形: (データ数, 1, 128, 32) ← チャンネル数「1」を追加
X_data = X_data[:, np.newaxis, :, :]

print("-" * 30)
print("データ読み込み完了！")
print(f"X_data shape: {X_data.shape}")  # (2031, 1, 128, 32) になるはず
print(f"y_label shape: {y_label.shape}")  # (2031,) になるはず
print("-" * 30)