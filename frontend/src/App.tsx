import { FormEvent, useMemo, useState } from "react";

import { search } from "./api";
import type { SearchResponse, UiState } from "./types";

export default function App() {
  const [query, setQuery] = useState("");
  const [state, setState] = useState<UiState>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [lastQuery, setLastQuery] = useState("");

  const canSubmit = useMemo(() => query.trim().length > 0 && state !== "loading", [query, state]);

  async function executeSearch(targetQuery: string) {
    setState("loading");
    setErrorMessage("");

    try {
      const response = await search({ query: targetQuery });
      setResult(response);
      setLastQuery(targetQuery);
      setState("success");
    } catch (error) {
      setState("error");
      setErrorMessage(error instanceof Error ? error.message : "検索中にエラーが発生しました。");
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) {
      return;
    }
    await executeSearch(trimmed);
  }

  async function onRetry() {
    const retryQuery = lastQuery || query.trim();
    if (!retryQuery) {
      return;
    }
    await executeSearch(retryQuery);
  }

  return (
    <main className="page">
      <section className="card">
        <h1>Cosense RAG QA</h1>
        <form className="search-form" onSubmit={onSubmit}>
          <textarea
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="質問を入力してください"
            rows={4}
            disabled={state === "loading"}
          />
          <button type="submit" disabled={!canSubmit}>
            {state === "loading" ? "検索中..." : "質問する"}
          </button>
        </form>
      </section>

      {state === "idle" && <section className="card">質問を入力して検索を実行してください。</section>}

      {state === "loading" && <section className="card">回答を生成しています...</section>}

      {state === "error" && (
        <section className="card error">
          <p>{errorMessage || "エラーが発生しました。"}</p>
          <button type="button" onClick={onRetry}>
            再試行
          </button>
        </section>
      )}

      {state === "success" && result && (
        <section className="card">
          <h2>回答</h2>
          <p className="answer">{result.answer}</p>
          <h3>citation</h3>
          {result.citations.length === 0 ? (
            <p>参照情報はありません。</p>
          ) : (
            <ul className="citations">
              {result.citations.map((citation) => (
                <li key={`${citation.url}-${citation.title}`}>
                  <a href={citation.url} target="_blank" rel="noreferrer">
                    {citation.title}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </main>
  );
}
