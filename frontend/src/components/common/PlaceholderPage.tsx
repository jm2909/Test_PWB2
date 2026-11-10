interface PlaceholderPageProps {
  title: string;
}

/** Temporary body for routes whose page a later UI task replaces. */
export default function PlaceholderPage({ title }: PlaceholderPageProps) {
  return (
    <section aria-labelledby="placeholder-h">
      <h1 id="placeholder-h" className="text-[2rem] leading-10">
        {title}
      </h1>
      <p className="mt-2 text-base text-text-secondary">This page is not available yet.</p>
    </section>
  );
}
