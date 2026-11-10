interface Props {
  text: string;
  readingCount?: number;
  sourceLabel?: string;
  unavailable?: boolean;
  loading?: boolean;
}

export default function ExplanationTile({ text, readingCount, sourceLabel, unavailable = false, loading = false }: Props) {
  return (
    <aside aria-labelledby="mean-h">
      <div className="bg-layer p-4" role="status">
        <h2 id="mean-h" className="text-base font-semibold">What this means</h2>
        <p className="mt-3">{loading ? 'Loading explanation…' : text}</p>
        {!loading && unavailable && (
          <p className="mt-3 text-xs text-[#6f6f6f]">Your readings are still shown so you can follow them yourself.</p>
        )}
        {!loading && !unavailable && readingCount !== undefined && readingCount > 0 && sourceLabel && (
          <p className="mt-4 text-xs text-[#6f6f6f]">
            Based on {readingCount} readings from {sourceLabel.toLowerCase()}.
          </p>
        )}
      </div>
    </aside>
  );
}
