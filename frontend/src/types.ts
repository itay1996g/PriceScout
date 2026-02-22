export interface SearchResult {
  rank: number;
  product_name: string;
  price: string;
  currency: string;
  seller_name: string;
  seller_address: string;
  url: string;
  condition: string;
  notes: string;
}

export interface SearchResponse {
  product_understood: string;
  location: string;
  results: SearchResult[];
  search_summary: string;
}

export type SearchStatus = "idle" | "searching" | "analyzing" | "complete" | "error";

export interface SearchEvent {
  status: SearchStatus;
  message?: string;
  data?: SearchResponse;
}
