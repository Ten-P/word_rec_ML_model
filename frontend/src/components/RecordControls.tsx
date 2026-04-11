// propsの型を明示的に定義する（暗黙のany防止）
type RecordControlsProps = {
  isRecording: boolean;
  onRecord: () => void;
  onStop: () => void;
};

export function RecordControls({ onRecord, onStop, isRecording }: RecordControlsProps) {
  return (
    <div id="buttons">
      {/* isRecordingの状態に応じてボタンの活性/非活性を制御 */}
      <button onClick={onRecord} disabled={isRecording}>
        Record
      </button>
      <button onClick={onStop} disabled={!isRecording}>
        Stop
      </button>
      <p>{isRecording ? "録音中..." : "待機中"}</p>
    </div>
  );
}
