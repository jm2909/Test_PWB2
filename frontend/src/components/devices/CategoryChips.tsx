import { categoryLabel } from '../../types/device';

export default function CategoryChips({ categories }: { categories: string[] }) {
  return (
    <ul className="mt-2 flex flex-wrap gap-2" aria-label="Permitted data categories">
      {categories.map((c) => (
        <li key={c} className="rounded-full bg-[#e0e0e0] px-2 text-xs leading-4 text-[#161616]">
          {categoryLabel(c)}
        </li>
      ))}
    </ul>
  );
}
