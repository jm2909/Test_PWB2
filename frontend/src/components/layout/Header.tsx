import { useAuth } from '../../lib/auth-context';

export default function Header() {
  const { user, logout } = useAuth();
  return (
    <header className="flex h-12 items-center gap-4 border-b border-[#393939] bg-[#161616] px-4 text-[#f4f4f4]">
      <span className="font-semibold tracking-[.1px]">
        <span className="font-normal">Sapphire</span> FitConnect
      </span>
      <span className="flex-1" />
      {user && <span className="text-[#c6c6c6]">{user.email}</span>}
      {user && (
        <button
          type="button"
          onClick={() => void logout()}
          className="h-8 border border-[#8d8d8d] bg-transparent px-4 text-[#f4f4f4]"
        >
          Sign out
        </button>
      )}
    </header>
  );
}
