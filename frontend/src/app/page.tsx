"use client";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import { RecordControls } from "@/components/RecordControls";
import { AudioClip } from "@/components/AudioClip";
import { InferenceResult } from "@/components/InferenceResult";

export default function Page() {
  const {
    isRecording,
    stopped,
    audioURL,
    clipName,
    result,
    isLoading,
    onClickRecord,
    onClickStop,
    onClickDelete,
  } = useAudioRecorder();

  return (
    <div className="wrapper">
      <header>
        <h1>Word Rec ML</h1>
      </header>

      <RecordControls
        isRecording={isRecording}
        onRecord={onClickRecord}
        onStop={onClickStop}
      />

      {/* stopped かつ audioURL がある場合だけ表示 */}
      {stopped && audioURL && (
        <AudioClip
          audioURL={audioURL}
          clipName={clipName}
          onDelete={onClickDelete}
        />
      )}

      <InferenceResult result={result} isLoading={isLoading} />
    </div>
  );
}

  