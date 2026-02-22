import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

interface HomeProps {
  onSearch: (query: string) => void;
  isSearching: boolean;
  searchesRemaining?: number;
}

const EXAMPLES = [
  "MacBook Pro M3 in Berlin",
  "Nike Air Max 90 in Seoul",
  "Canon R5 camera in New York",
  "2020 Omega Speedmaster in Tokyo",
];

export function Home({ onSearch, isSearching, searchesRemaining }: HomeProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <div className="flex flex-col items-center justify-center px-6 pt-32">
      <h1 className="text-5xl font-bold text-slate-900 mb-3">
        Find the Best Deal
      </h1>
      <p className="text-lg text-slate-500 mb-10">
        Anywhere in the World
      </p>

      <form onSubmit={handleSubmit} className="w-full max-w-xl flex gap-2">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What are you looking for? e.g. 2020 Omega Speedmaster in Tokyo"
          className="h-12 text-base"
          disabled={isSearching}
        />
        <Button type="submit" size="lg" disabled={isSearching || !query.trim()}>
          <Search className="w-4 h-4" />
        </Button>
      </form>

      <div className="mt-6 flex flex-wrap gap-2 justify-center">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => {
              setQuery(ex);
              onSearch(ex);
            }}
            className="text-sm text-slate-400 hover:text-slate-600 transition-colors"
            disabled={isSearching}
          >
            {ex}
          </button>
        ))}
      </div>

      {searchesRemaining !== undefined && searchesRemaining >= 0 && (
        <p className="mt-16 text-sm text-slate-400">
          {searchesRemaining} free search{searchesRemaining !== 1 ? "es" : ""} remaining
        </p>
      )}
    </div>
  );
}
