import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { Home } from "@/pages/Home";
import { Results } from "@/pages/Results";
import { useSearch } from "@/hooks/useSearch";

function App() {
  const { status, message, results, search, reset } = useSearch();
  const isSearching = status === "searching" || status === "analyzing";
  const showResults = status === "complete" || isSearching;

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route
            path="/"
            element={
              showResults ? (
                <Results
                  status={status}
                  message={message}
                  results={results}
                  onNewSearch={reset}
                />
              ) : (
                <Home onSearch={search} isSearching={isSearching} />
              )
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
