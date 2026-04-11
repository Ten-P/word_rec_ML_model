"use client";
import { useEffect, useRef, useState } from "react";
import { InferenceResult } from "@/types";

// このフックが外部に公開する値と関数の型
type UseAudioRecorderReturn = {
  isSupported: boolean;   // マイクが使えるか
  isRecording: boolean;   // 録音中か
  stopped: boolean;       // 録音が完了したか
  audioURL: string | undefined;   // 録音音声のURL（ブラウザ再生用）
  clipName: string | undefined;   // クリップ名
  result: InferenceResult | null; // 推論結果
  isLoading: boolean;             // 推論中か
  onClickRecord: () => void;
  onClickStop: () => void;
  onClickDelete: () => void;
};

export function useAudioRecorder(): UseAudioRecorderReturn {
  const [isSupported, setIsSupported] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder>();
  const [stopped, setStopped] = useState(false);
  const chunksRef = useRef<BlobPart[]>([]);
  const [audioURL, setAudioURL] = useState<string>();
  const [isRecording, setIsRecording] = useState(false);
  const [clipName, setClipName] = useState<string>();
  const [result, setResult] = useState<InferenceResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(
      async (stream) => {
        setIsSupported(true);
        const rec = new MediaRecorder(stream);
        setMediaRecorder(rec);

        // データが届くたびにchunksRefに追加
        rec.ondataavailable = (e: BlobEvent) => {
          chunksRef.current.push(e.data);
        };

        // 録音停止時: Blob作成 → API送信 → 推論結果をstateに保存
        rec.onstop = async () => {
          if (chunksRef.current.length === 0) return;

          const name = prompt("Enter a name for your sound clip?", "My unnamed clip");
          const resolvedName = name ?? "My unnamed clip";
          setClipName(resolvedName);

          const blob = new Blob(chunksRef.current, { type: rec.mimeType });
          const audioURL = window.URL.createObjectURL(blob);
          setAudioURL(audioURL);

          const formData = new FormData();
          formData.append("audio", blob, "recording.webm");
          formData.append("name", resolvedName);

          setIsLoading(true);
          setResult(null);
          try {
            const res = await fetch("api/transcri", {
              method: "POST",
              body: formData,
            });
            const result = (await res.json()) as InferenceResult;
            setResult(result);
          } finally {
            setIsLoading(false);
          }

          chunksRef.current = [];
        };
      },
      () => {
        setIsSupported(false);
      }
    );
  }, []);

  const onClickRecord = () => {
    mediaRecorder?.start();
    setIsRecording(true);
    setStopped(false);
    setResult(null);
  };

  const onClickStop = () => {
    mediaRecorder?.stop();
    setStopped(true);
    setIsRecording(false);
  };

  const onClickDelete = () => {
    setStopped(false);
    setResult(null);
    setAudioURL(undefined);
    setClipName(undefined);
  };

  return {
    isSupported,
    isRecording,
    stopped,
    audioURL,
    clipName,
    result,
    isLoading,
    onClickRecord,
    onClickStop,
    onClickDelete,
  };
}
