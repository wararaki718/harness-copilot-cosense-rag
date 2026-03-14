export type UiState = "idle" | "loading" | "success" | "error";

export interface SearchRequest {
  query: string;
  top_k?: number;
  score_threshold?: number;
}

export interface Citation {
  title: string;
  url: string;
}

export interface SearchResponse {
  answer: string;
  citations: Citation[];
}
