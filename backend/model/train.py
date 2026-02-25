import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from ML_model import CNN

# ====================================================
# 1. データの読み込みと整形
# ====================================================
# 保存したファイルを読み込む
data = np.load("processed_data_split.npz")

x_train = data['x_train']
x_test = data['x_test']
t_train = data['t_train']
t_test = data['t_test']
classes = data['classes']

# 【重要】CNN用にデータを4次元に整形 (N, 1, 128, 32)
# すでに4次元ならこの処理は無視されますが、念のため入れておくと安全です
if x_train.ndim == 3:
    x_train = x_train.reshape(-1, 1, 128, 32)
    x_test = x_test.reshape(-1, 1, 128, 32)

print(f"学習データ: {x_train.shape}")
print(f"テストデータ: {x_test.shape}")
print(f"クラス数: {len(classes)}")

# ====================================================
# 2. ネットワークの生成
# ====================================================
network = CNN(
    input_dim=(1, 128, 32), 
    hidden_size=100, 
    output_size=len(classes)
)

# ===========================
# 3. ハイパーパラメータの設定 
# ==========================
learning_rate = 0.01
iters_num = 20000

train_size = x_train.shape[0]

iter_per_epoch = max(train_size / batch_size, 1) #データ量全体にたいしてサンプルの大きさ何個ぶんか

train_loss_list = []
train_acc_list = []
test_acc_list = []

# Momentum用の速度(v)を初期化
velocity = {}
for key in network.params.keys():
    velocity[key] = np.zeros_like(network.params[key])

print(f"--- 学習開始 (LR={learning_rate}, Iters={iters_num}) ---")
best_acc = 0.0
# ====================================================
# 4. 学習ループ
# ====================================================
for i in range(iters_num):
    
    if i == 10000:
        learning_rate *= 0.1
        print(f"学習率変更")
        
    # ミニバッチの取得
    batch_mask = np.random.choice(train_size, batch_size)
    x_batch = x_train[batch_mask]
    t_batch = t_train[batch_mask]
    
    # --- 1. ホワイトノイズの追加 ---
    noise = np.random.randn(*x_batch.shape) * 0.01
    x_batch = x_batch + noise

    # --- 2. SpecAugment (時間・周波数のマスキング) ---
    # 周波数マスキング (Frequency Masking)
    # 128ピクセル（高さ）のうち、ランダムに8ピクセル分を「無音」にする
    f_mask_width = 4
    f0 = np.random.randint(0, 128 - f_mask_width)
    x_batch[:, :, f0:f0+f_mask_width, :] = 0

    # 時間マスキング (Time Masking)
    # 32ピクセル（幅）のうち、ランダムに4ピクセル分を「無音」にする
    t_mask_width = 2
    t0 = np.random.randint(0, 32 - t_mask_width)
    x_batch[:, :, :, t0:t0+t_mask_width] = 0

    grad = network.gradient(x_batch, t_batch)

    # Momentum SGD による更新
    momentum = 0.9
    for key in network.params.keys():
        velocity[key] = momentum * velocity[key] - learning_rate * grad[key]
        network.params[key] += velocity[key]

    # 誤差の記録
    loss = network.loss(x_batch, t_batch, train_flg=True)
    train_loss_list.append(loss)

    # 1エポックごとに進捗を表示
    if i % int(iter_per_epoch) == 0:
        # 時間がかかるので5000件くらいで評価してもOKですが、正確に見るなら全件推奨
        train_acc = network.accuracy(x_train[:2000], t_train[:2000], batch_size=batch_size)
        test_acc = network.accuracy(x_test[:2000], t_test[:2000], batch_size=batch_size)
        
        train_acc_list.append(train_acc)
        test_acc_list.append(test_acc)
        
        print(f"Epoch {int(i/iter_per_epoch)} | Loss: {loss:.4f} | Train Acc: {train_acc:.4f} | Test Acc: {test_acc:.4f}")
        
        if test_acc > best_acc:
            best_acc = test_acc  # 最高記録を更新！
            network.save_params("best_params.pkl")  # ファイルに保存
            print(f"★ 最高記録更新！保存しました (Acc: {best_acc:.4f})")

# (以下、保存とグラフ描画は同じ)



"""
--- 学習開始 (LR=0.01, Iters=20000) ---
Epoch 0 | Loss: 3.6142 | Train Acc: 0.0200 | Test Acc: 0.0195
★ 最高記録更新！保存しました (Acc: 0.0195)
Epoch 0 | Loss: 1.9667 | Train Acc: 0.5105 | Test Acc: 0.4975
★ 最高記録更新！保存しました (Acc: 0.4975)
Epoch 1 | Loss: 1.7409 | Train Acc: 0.6445 | Test Acc: 0.6200
★ 最高記録更新！保存しました (Acc: 0.6200)
Epoch 2 | Loss: 1.2024 | Train Acc: 0.7075 | Test Acc: 0.6735
★ 最高記録更新！保存しました (Acc: 0.6735)
Epoch 3 | Loss: 1.1051 | Train Acc: 0.6495 | Test Acc: 0.6270
Epoch 4 | Loss: 0.9295 | Train Acc: 0.7975 | Test Acc: 0.7525
★ 最高記録更新！保存しました (Acc: 0.7525)
Epoch 5 | Loss: 0.9901 | Train Acc: 0.8035 | Test Acc: 0.7560
★ 最高記録更新！保存しました (Acc: 0.7560)
Epoch 6 | Loss: 0.7255 | Train Acc: 0.7990 | Test Acc: 0.7675
★ 最高記録更新！保存しました (Acc: 0.7675)
Epoch 7 | Loss: 0.8140 | Train Acc: 0.8320 | Test Acc: 0.7835
★ 最高記録更新！保存しました (Acc: 0.7835)
Epoch 8 | Loss: 1.0689 | Train Acc: 0.8335 | Test Acc: 0.7815
Epoch 9 | Loss: 0.5864 | Train Acc: 0.8530 | Test Acc: 0.8055
★ 最高記録更新！保存しました (Acc: 0.8055)
Epoch 10 | Loss: 0.7250 | Train Acc: 0.8550 | Test Acc: 0.7990
Epoch 11 | Loss: 0.6299 | Train Acc: 0.8550 | Test Acc: 0.7940
Epoch 12 | Loss: 0.6384 | Train Acc: 0.8840 | Test Acc: 0.8170
★ 最高記録更新！保存しました (Acc: 0.8170)
Epoch 13 | Loss: 0.4919 | Train Acc: 0.8940 | Test Acc: 0.8300
★ 最高記録更新！保存しました (Acc: 0.8300)
Epoch 14 | Loss: 0.5591 | Train Acc: 0.9015 | Test Acc: 0.8265

★ 学習率を下げました！ (LR: 0.02 -> 0.0010) 

Epoch 15 | Loss: 0.4741 | Train Acc: 0.9050 | Test Acc: 0.8370
★ 最高記録更新！保存しました (Acc: 0.8370)
Epoch 16 | Loss: 0.4597 | Train Acc: 0.9110 | Test Acc: 0.8340
Epoch 17 | Loss: 0.4180 | Train Acc: 0.9140 | Test Acc: 0.8345
Epoch 18 | Loss: 0.5751 | Train Acc: 0.9125 | Test Acc: 0.8400
★ 最高記録更新！保存しました (Acc: 0.8400)
Epoch 19 | Loss: 0.4012 | Train Acc: 0.9125 | Test Acc: 0.8365
Epoch 20 | Loss: 0.5566 | Train Acc: 0.9025 | Test Acc: 0.8300
"""