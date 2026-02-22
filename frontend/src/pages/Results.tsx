import { Button } from "@/components/ui/button";
import { SearchProgress } from "@/components/SearchProgress";
import { ResultCard } from "@/components/ResultCard";
import type { SearchResponse, SearchStatus } from "@/types";
import { RotateCcw } from "lucide-react";

interface ResultsProps {
  status: SearchStatus;
  message: string;
  results: SearchResponse | null;
  onNewSearch: () => void;
}

export function Results({ status, message, results, onNewSearch }: ResultsProps) {
  if (status === "searching" || status === "analyzing") {
    return <SearchProgress status={status} message={message} />;
  }

  if (!results || results.results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center pt-32 px-6">
        <p className="text-slate-500 text-lg">
          No results found. Try a different search.
        </p>
        <Button variant="outline" className="mt-6" onClick={onNewSearch}>
          <RotateCcw className="w-4 h-4 mr-2" /> New Search
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-6 pt-12 pb-16">
      <p className="text-sm text-slate-400 mb-1">
        {results.product_understood} in {results.location}
      </p>
      <div className="flex flex-col gap-4 mt-4">
        {results.results.map((result) => (
          <ResultCard key={result.rank} result={result} />
        ))}
      </div>
      <p className="text-sm text-slate-400 text-center mt-6">
        {results.search_summary}
      </p>
      <div className="flex justify-center mt-6">
        <Button variant="outline" onClick={onNewSearch}>
          <RotateCcw className="w-4 h-4 mr-2" /> New Search
        </Button>
      </div>
    </div>
  );
}
