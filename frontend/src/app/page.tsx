"use client";
import { useEffect, useState } from "react";

export default function Page() {
  const [isSupported, setIsSupported] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder>();
  const [stopped, setStopped] = useState(false);
  const [chunks, setChunks] = useState<BlobPart[]>([]);
  const [audioURL, setAudioURL] = useState<string>();
  const [isRecording, setIsRecording] = useState(false);
  const [clipName, setClipName] = useState<string>();
  const [blob, setBlob] = useState<Blob>();

  
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(
      async (stream) => {
        setIsSupported(true);
        const rec = new MediaRecorder(stream);
        setMediaRecorder(rec);

        rec.ondataavailable = async (e: BlobEvent) => {
          setChunks((prev) => [...prev, e.data]);
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

  useEffect(() => {
    if (stopped && chunks.length > 0) {
      onDataAvailable();
    }
  }, [chunks]);

  async function onDataAvailable()  {
    const clipName = prompt(
      "Enter a name for your sound clip?",
      "My unnamed clip"
    );

    if (clipName === null) {
      setClipName("My unnamed clip");
    } else {
      setClipName(clipName);
    }

    const blob = new Blob(chunks, { type: mediaRecorder?.mimeType });

    const audioURL = window.URL.createObjectURL(blob);
    setBlob(blob);
    setAudioURL(audioURL);
    console.log("recorder stopped");

    const formData = new FormData();
    const resolveddName = clipName ?? "My unnamed clip"
    formData.append("audio", blob!, "recording.webm");
    formData.append("name", resolveddName);
    
    await fetch("api/transcri", {
      method: "POST",
      body: formData
    });

  };

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
        </section>
      </div>
    </div>
  );
}