"use client";
import { useEffect, useState, useRef } from "react";

type InferenceResult = {
  filename: string;
  top_result: { label: string; prob: string };
  other_candidates: { label: string; prob: string }[];
  message: string;
};

export default function Page() {
  const [isSupported, setIsSupported] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder>();
  const [stopped, setStopped] = useState(false);
  const chunksRef = useRef<BlobPart[]>([]);
  const [audioURL, setAudioURL] = useState<string>();
  const [isRecording, setIsRecording] = useState(false);
  const [clipName, setClipName] = useState<string>();
  const [blob, setBlob] = useState<Blob>();
  const [result, setResult] = useState<InferenceResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  

  
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(
      async (stream) => {
        setIsSupported(true);
        const rec = new MediaRecorder(stream);
        setMediaRecorder(rec);

        rec.ondataavailable = (e: BlobEvent) => {
          chunksRef.current.push(e.data);
        };

        rec.onstop = async () => {
          if (chunksRef.current.length === 0) return;

          const name = prompt(
            "Enter a name for your sound clip?",
            "My unnamed clip"
          );
          const resolvedName = name ?? "My unnamed clip";
          setClipName(resolvedName);

          const blob = new Blob(chunksRef.current, { type: rec.mimeType });
          const audioURL = window.URL.createObjectURL(blob);
          setBlob(blob);
          setAudioURL(audioURL);
          console.log("recorder stopped");

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
            const result = await res.json() as InferenceResult;
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
    console.log("Recorder started.");
    setIsRecording(true);
  }

  const onClickStop = () => {
    mediaRecorder?.stop();
    console.log("Recorder stopped.");
    setStopped(true);
    setIsRecording(false);
  }

  return (
    <div>
      <div className="wrapper">
        <header>
          <h1>Word Rec ML</h1>
        </header>
        <section className="main-controls">
          <canvas className="visualizer" height="60px"></canvas>
          <div id="buttons">
            <button className="record" onClick={onClickRecord}>
              Record
            </button>
            <button className="stop" onClick={onClickStop}>
              Stop
            </button>
          </div>
        </section>
        {isRecording ? "Recording" : "Not Recording"}
        <section className="sound-clips">
          {stopped ? (
            <article className="clip">
              <audio src={audioURL} controls></audio>
              <p>{clipName}</p>
              <button className="delete" onClick={() => setStopped(false)}>
                Delete
              </button>
            </article>
          ) : (
            <></>
          )}
        </section>   {/* ← sound-clipsのsectionの閉じタグ */}

        {/* ローディング中メッセージ */}
        {isLoading && (
          <section>
            <p>推論中です。しばらくお待ちください...</p>
          </section>
        )}

        {/* 推論結果の表示 */}
        {!isLoading && result && (
          <section>
            <p>{result.message}</p>
            <p>他の候補:</p>
            <ul>
              {result.other_candidates.map((c) => (
                <li key={c.label}>{c.label}: {c.prob}</li>
              ))}
            </ul>
          </section>
        )}

      </div>
    </div>
  );
}