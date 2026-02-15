import sys, os
sys.path.append(os.pardir)  # 親ディレクトリのファイルをインポートできるようにする
import numpy as np
import matplotlib.pyplot as plt
from dataset.mnist import load_mnist
from simple_conv_net import SimpleConvNet

# CNNなので、画像を平らにせず(1, 28, 28)のまま読み込む (flatten=False)
print("データを読み込んでいます...")
(x_train, t_train), (x_test, t_test) = load_mnist(flatten=False)

#バッチテストの場合
# x_train, t_train = x_train[:5000], t_train[:5000]
# x_test, t_test = x_test[:1000], t_test[:1000]


max_epochs = 20
network = SimpleConvNet(input_dim=(1,28,28), 
                        conv_param = {'filter_num': 30, 'filter_size': 5, 'pad': 0, 'stride': 1},
                        hidden_size=100, output_size=10, weight_init_std=0.01)

# 3. ハイパーパラメータの設定
iters_num = 10000  # 繰り返す回数
train_size = x_train.shape[0]
batch_size = 100   # 一度に計算する画像の枚数
learning_rate = 0.001

train_loss_list = []
train_acc_list = []
test_acc_list = []

iter_per_epoch = max(train_size / batch_size, 1)

print("学習を開始します...")


for i in range(iters_num):
    
    batch_mask = np.random.choice(train_size, batch_size)
    x_batch = x_train[batch_mask]
    t_batch = t_train[batch_mask]


    grads = network.gradient(x_batch, t_batch)

    #SDG
    for key in ('W1', 'b1', 'W2', 'b2', 'W3', 'b3'):
        network.params[key] -= learning_rate * grads[key]

    loss = network.loss(x_batch, t_batch)
    train_loss_list.append(loss)

    if i % iter_per_epoch == 0:
        train_acc = network.accuracy(x_train, t_train, batch_size=500) # 時間がかかるならbatch_size調整
        test_acc = network.accuracy(x_test, t_test, batch_size=500)
        train_acc_list.append(train_acc)
        test_acc_list.append(test_acc)
        print(f"Epoch: {int(i/iter_per_epoch)}, Train acc: {train_acc:.4f}, Test acc: {test_acc:.4f}, Loss: {loss:.4f}")

print("学習終了！")

#パラメータの保存
network.save_params("params.pkl")
print("パラメータを params.pkl に保存しました。")