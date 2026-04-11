type AudioClipProps = {
    audioURL: string;
    clipName: string | undefined;
    onDelete: () => void;
}

export function AudioClip({ audioURL, clipName, onDelete }: AudioClipProps) {
    return (
        <article className="clip">
            <audio src={audioURL} controls />
            <p>{clipName}</p>
            <button className="delete" onClick={onDelete}>
                Delete
            </button>
        </article>
    )
}