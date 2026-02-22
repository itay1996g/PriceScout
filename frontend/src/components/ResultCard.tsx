import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExternalLink } from "lucide-react";
import type { SearchResult } from "@/types";

interface ResultCardProps {
  result: SearchResult;
}

const RANK_LABELS: Record<number, { label: string; color: string }> = {
  1: { label: "Best Price", color: "bg-yellow-100 text-yellow-800" },
  2: { label: "Runner Up", color: "bg-slate-100 text-slate-700" },
  3: { label: "Also Great", color: "bg-orange-50 text-orange-700" },
};

export function ResultCard({ result }: ResultCardProps) {
  const rank = RANK_LABELS[result.rank] || RANK_LABELS[3];

  return (
    <Card className="w-full">
      <CardContent className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <Badge className={rank.color} variant="secondary">
              {rank.label}
            </Badge>
            <h3 className="mt-2 text-lg font-semibold text-slate-900">
              {result.product_name}
            </h3>
            <p className="text-2xl font-bold text-slate-900 mt-1">
              {result.price}
            </p>
            <p className="text-sm text-slate-500 mt-2">
              {result.seller_name} &middot; {result.seller_address}
            </p>
            {result.condition && (
              <p className="text-sm text-slate-400 mt-1">
                Condition: {result.condition}
              </p>
            )}
            {result.notes && (
              <p className="text-sm text-slate-400 mt-1">{result.notes}</p>
            )}
          </div>
          <a href={result.url} target="_blank" rel="noopener noreferrer">
            <Button variant="outline" size="sm">
              View Deal <ExternalLink className="w-3 h-3 ml-1" />
            </Button>
          </a>
        </div>
      </CardContent>
    </Card>
  );
}
