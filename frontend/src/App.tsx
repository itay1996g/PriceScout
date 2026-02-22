import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { Home } from "@/pages/Home";
import { Results } from "@/pages/Results";
import { Login } from "@/pages/Login";
import { Register } from "@/pages/Register";
import { useSearch } from "@/hooks/useSearch";
import { PaywallModal } from "@/components/PaywallModal";

function App() {
  const { status, message, results, error, search, reset } = useSearch();
  const isSearching = status === "searching" || status === "analyzing";
  const showResults = status === "complete" || isSearching;
  const showPaywall = error === "quota_exceeded";

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
        <PaywallModal open={showPaywall} onClose={reset} />
      </Layout>
    </BrowserRouter>
  );
}

export default App;
