"use client";
import React, { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { InferenceResult } from "@/types";

// このフックが外部に公開する値と関数の型
type UseAudioRecorderReturn = {
  isSupported: boolean;
  isRecording: boolean;
  isLoading: boolean;
  remainingTime: number;  // 残り録音時間(秒)
  recordDuration: number; // 最大録音時間(秒)
  analyserRef: React.RefObject<AnalyserNode | null>;
  onClickRecord: () => void;
};

// デフォルトの録音秒数
const DEFAULT_RECORD_DURATION = 3;

export function useAudioRecorder(): UseAudioRecorderReturn {
  const router = useRouter();
  const [isSupported, setIsSupported] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder>();
  const chunksRef = useRef<BlobPart[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [remainingTime, setRemainingTime] = useState(DEFAULT_RECORD_DURATION);
  // 自動停止用タイマーのref（cancelできるよう保持）
  const stopTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);
  // Web Audio API: 波形データを取り出すためのノード
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(
      async (stream) => {
        setIsSupported(true);
        const rec = new MediaRecorder(stream);
        setMediaRecorder(rec);

        // Web Audio API: ストリームをAnalyserNodeに接続して波形データを取得できるようにする
        const audioContext = new AudioContext();
        audioContextRef.current = audioContext;
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048; // 波形の解像度（大きいほど細かい）
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser); // マイク → AnalyserNode
        analyserRef.current = analyser;

        // データが届くたびにchunksRefに追加
        rec.ondataavailable = (e: BlobEvent) => {
          chunksRef.current.push(e.data);
        };

        // 録音停止時: Blob作成 → API送信 → 推論結果をstateに保存
        rec.onstop = async () => {
          if (chunksRef.current.length === 0) return;

          const resolvedName = "audio_data";

          const blob = new Blob(chunksRef.current, { type: rec.mimeType });

          const formData = new FormData();
          formData.append("audio", blob, "recording.webm");
          formData.append("name", resolvedName);

          setIsLoading(true);
          try {
            const res = await fetch("api/transcri", {
              method: "POST",
              body: formData,
            });
            const result = (await res.json()) as InferenceResult;
            // 結果をsessionStorageに保存してから結果ページへ遷移
            // sessionStorage: ブラウザタブを閉じると消える一時保存領域
            sessionStorage.setItem("inferenceResult", JSON.stringify(result));
            router.push("/result");
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
    setRemainingTime(DEFAULT_RECORD_DURATION);

    // 1秒ごとに残り時間を減らすカウントダウン
    countdownRef.current = setInterval(() => {
      setRemainingTime((prev) => Math.max(0, prev - 1));
    }, 1000);

    // DEFAULT_RECORD_DURATION 秒後に自動停止
    stopTimerRef.current = setTimeout(() => {
      mediaRecorder?.stop();
      setIsRecording(false);
      if (countdownRef.current) clearInterval(countdownRef.current);
    }, DEFAULT_RECORD_DURATION * 1000);
  };

  return {
    isSupported,
    isRecording,
    isLoading,
    remainingTime,
    recordDuration: DEFAULT_RECORD_DURATION,
    analyserRef,
    onClickRecord,
  };
}
