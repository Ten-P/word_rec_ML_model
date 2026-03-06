#実行時docker exec -it my-ml-container python3 /app/torchmodel/test.py


import os
import librosa
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader


DATASET_PATH = "/app/dataset" 
SR = 16000
N_MELS = 128
TARGET_WIDTH = 32



class CustomAudioDataset(Dataset):
    def __init__(self, dataset_dir):
        self.file_paths = []
        self.labels = []
        
        self.classes = sorted([d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))])
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}
        
        for class_name in self.classes:
            class_dir = os.path.join(dataset_dir, class_name)
            label_id = self.class_to_idx[class_name]
            
            for file_name in os.listdir(class_dir):
                if file_name.endswith(('.wav', '.mp3')):
                    self.file_paths.append(os.path.join(class_dir, file_name))
                    self.labels.append(label_id)

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        file_path = self.file_paths[idx]
        label = self.labels[idx]
        
        # 音声読み込み(numpy.ndarray)
        y, _ = librosa.load(file_path, sr=SR)
        
        #正規化
        max_val = np.max(np.abs(y))
        if max_val > 0:
            y = y / max_val
            
        #メルスペクトログラム変換(numpy.ndarray (2次元)縦128固定の画像に変換)
        S = librosa.feature.melspectrogram(y=y, sr=SR, n_mels=N_MELS, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        #幅の調整 (TARGET_WIDTHにする)
        current_width = S_dB.shape[1]
        if current_width < TARGET_WIDTH:
            pad_width = TARGET_WIDTH - current_width
            S_fixed = np.pad(S_dB, ((0, 0), (0, pad_width)), mode='constant')
        else:
            S_fixed = S_dB[:, :TARGET_WIDTH]
            
        #テンソルに変換 (Channel, Height, Width) の形にする
        #unsqueeze(0)で（123,32）-> (1,128,32)
        tensor_data = torch.from_numpy(S_fixed).float().unsqueeze(0)
        tensor_label = torch.tensor(label).long()
        
        return tensor_data, tensor_label




full_dataset = CustomAudioDataset(DATASET_PATH)

#学習用とテスト用に分割 (8:2)
train_size = int(0.8 * len(full_dataset))
test_size = len(full_dataset) - train_size
train_dataset, test_dataset = torch.utils.data.random_split(full_dataset, [train_size, test_size])

#ベルトコンベア（DataLoader）の作成
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)


print(f"全データ数: {len(full_dataset)}")
print(f"クラス一覧: {full_dataset.classes}")

#ここで初めてテンソルになる
for images, labels in train_loader:
    print(f"バッチ内のデータの形: {images.shape}") # (32, 1, 128, 32)
    print(f"バッチ内のラベル: {labels}")
    break










def save_preprocessed_data():
    dataset = CustomAudioDataset(DATASET_PATH)
    
    all_features = []
    all_labels = []

    print(f"変換開始... (全 {len(dataset)} ファイル)")
    
    # --- 1. ループの中でしっかりデータを集める ---
    for i in range(len(dataset)):
        # ここで実際に音声を読み込んで変換する
        data, label = dataset[i]
        all_features.append(data)
        all_labels.append(label)

        if i % 1000 == 0: # 100件だと表示が多すぎるので1000にしました
            print(f"変換中: {i}/{len(dataset)}")

    # --- 2. 【重要】ここから下のインデントを左に寄せる（ループの外へ！） ---
    print(f"全データの変換完了。テンソルにまとめます（ここが少し重いです）...")
    
    # リストを1つの大きなテンソルにまとめる
    x_tensor = torch.stack(all_features)
    t_tensor = torch.stack(all_labels)

    # まとめて保存
    save_path = "processed_audio_data.pt"
    torch.save({
        'x': x_tensor,
        't': t_tensor,
        'classes': dataset.classes
    }, save_path)

    print(f"保存完了！ ファイル名: {save_path}")
    print(f"データの形: {x_tensor.shape}")

if __name__ == "__main__":
    save_preprocessed_data()