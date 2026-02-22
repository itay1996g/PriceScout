import { useState, useCallback } from "react";
import type { SearchResponse, SearchStatus, SearchEvent } from "@/types";

export function useSearch() {
  const [status, setStatus] = useState<SearchStatus>("idle");
  const [message, setMessage] = useState("");
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string) => {
    setStatus("searching");
    setMessage("Starting search...");
    setResults(null);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ query }),
      });

      if (res.status === 402) {
        setStatus("error");
        setError("quota_exceeded");
        return;
      }

      if (!res.ok) {
        throw new Error("Search request failed");
      }

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No response stream");

      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.slice(6);
            try {
              const event: SearchEvent = JSON.parse(jsonStr);
              setStatus(event.status);
              if (event.message) setMessage(event.message);
              if (event.data) setResults(event.data);
            } catch {
              // skip malformed events
            }
          }
        }
      }
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }, []);

  const reset = useCallback(() => {
    setStatus("idle");
    setMessage("");
    setResults(null);
    setError(null);
  }, []);

  return { status, message, results, error, search, reset };
}
