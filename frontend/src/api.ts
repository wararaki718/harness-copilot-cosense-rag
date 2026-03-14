import type { SearchRequest, SearchResponse } from "./types";

const baseUrl = import.meta.env.VITE_RETRIEVAL_API_BASE_URL ?? "http://localhost:8000";

export async function search(request: SearchRequest): Promise<SearchResponse> {
  const response = await fetch(`${baseUrl}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "検索リクエストに失敗しました。");
  }

  return (await response.json()) as SearchResponse;
}
