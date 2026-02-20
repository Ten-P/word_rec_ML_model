import sys, os
import glob
import numpy as np
import librosa
import matplotlib.pyplot as plt

# ==========================================
# データの読み込み関数（train.pyと同じもの）
# ==========================================
def load_and_visualize_dataset(num_samples=5):
    print(f"確認用に {num_samples} 枚だけ読み込みます...")
    
    # パスの設定
    current_dir = os.path.dirname(os.path.abspath(__file__))
    wav_dir = os.path.join(current_dir, '../dataset/jsut_ver1.1/basic5000/wav/*.wav')
    
    files = glob.glob(wav_dir)
    if len(files) == 0:
        print("エラー: ファイルが見つかりません。")
        sys.exit()

    # 指定した枚数だけピックアップ
    files = files[:num_samples]
    
    # 設定サイズ
    TARGET_HEIGHT = 128
    TARGET_WIDTH = 300

    loaded_images = []

    for i, file_path in enumerate(files):
        # 1. 音声読み込み
        y, sr = librosa.load(file_path, sr=None)
        
        # 2. スペクトログラム変換
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=TARGET_HEIGHT)
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        # 3. 正規化 (0.0 ~ 1.0)
        img = (S_dB - S_dB.min()) / (S_dB.max() - S_dB.min())

        # 4. サイズ合わせ (300に統一)
        current_width = img.shape[1]
        if current_width > TARGET_WIDTH:
            img = img[:, :TARGET_WIDTH] # カット
        else:
            pad_width = TARGET_WIDTH - current_width
            img = np.pad(img, ((0, 0), (0, pad_width)), mode='constant') # 埋める

        loaded_images.append(img)
        print(f"[{i+1}/{num_samples}] {os.path.basename(file_path)} を処理しました")

    return np.array(loaded_images)

# ==========================================
# メイン処理：データを表示する
# ==========================================

# 1. データをロード
data = load_and_visualize_dataset(num_samples=3)

# 2. 形（Shape）の確認
print("\n=== データの確認 ===")
print(f"全体の形 (N, H, W): {data.shape}")
print(f" -> 枚数: {data.shape[0]}枚")
print(f" -> 縦(高さ): {data.shape[1]} px")
print(f" -> 横(時間): {data.shape[2]} px")

# 3. 画像として表示（AIがこれを見ることになります）
print("\n画像を生成しています...")
plt.figure(figsize=(10, 6))

for i in range(len(data)):
    plt.subplot(len(data), 1, i+1) # 縦に並べる
    plt.imshow(data[i], aspect='auto', origin='lower', cmap='inferno')
    plt.title(f"Sample {i+1}")
    plt.axis('off') # 枠線を消す

plt.tight_layout()
plt.show()

print("表示完了！これがAIに入力されるデータです。")