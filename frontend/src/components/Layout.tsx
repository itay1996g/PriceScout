import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const token = localStorage.getItem("token");

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl flex items-center justify-between px-6 py-4">
          <Link to="/" className="text-xl font-bold text-slate-900">
            PriceScout
          </Link>
          {token ? (
            <Button
              variant="ghost"
              onClick={() => {
                localStorage.removeItem("token");
                window.location.reload();
              }}
            >
              Sign Out
            </Button>
          ) : (
            <Link to="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
          )}
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}
