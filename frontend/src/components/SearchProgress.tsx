import type { SearchStatus } from "@/types";

interface SearchProgressProps {
  status: SearchStatus;
  message: string;
}

export function SearchProgress({ status, message }: SearchProgressProps) {
  const progress = status === "searching" ? 40 : status === "analyzing" ? 75 : 100;

  return (
    <div className="w-full max-w-xl mx-auto mt-16 px-6">
      <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-slate-900 rounded-full transition-all duration-700 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="mt-3 text-sm text-slate-500 text-center">{message}</p>
    </div>
  );
}
