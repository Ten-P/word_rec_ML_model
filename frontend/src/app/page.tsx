"use client";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import { RecordControls } from "@/components/RecordControls";
import { WaveformVisualizer } from "@/components/WaveformVisualizer";

export default function Page() {
  const {
    isRecording,
    isLoading,
    remainingTime,
    recordDuration,
    analyserRef,
    onClickRecord,
  } = useAudioRecorder();

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center gap-8">
      <header className="text-center">
        <h1 className="text-4xl font-bold tracking-widest text-indigo-400">
          Word Rec ML
        </h1>
        <p className="text-gray-400 text-center mt-2 text-sm">
          音声を録音して単語を識別します
        </p>
      </header>

      {/* 波形 → ボタン の縦並びレイアウト */}
      <div className="flex flex-col items-center gap-6 w-full px-4">
        <WaveformVisualizer
          analyserRef={analyserRef}
          isRecording={isRecording}
          remainingTime={remainingTime}
          recordDuration={recordDuration}
        />
        <RecordControls
          isRecording={isRecording}
          isLoading={isLoading}
          onRecord={onClickRecord}
        />
      </div>

      {isLoading && (
        <p className="text-indigo-300 animate-pulse">
          推論中です。しばらくお待ちください...
        </p>
      )}
    </div>
  );
}



  