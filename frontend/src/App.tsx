import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { Home } from "@/pages/Home";
import { Results } from "@/pages/Results";
import { Login } from "@/pages/Login";
import { Register } from "@/pages/Register";
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
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
