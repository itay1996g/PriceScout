import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useState } from "react";

interface PaywallModalProps {
  open: boolean;
  onClose: () => void;
}

const FEATURES = [
  "Unlimited searches",
  "Priority agent speed",
  "Detailed price breakdowns",
];

export function PaywallModal({ open, onClose }: PaywallModalProps) {
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem("token");

  const handleSubscribe = async () => {
    if (!token) {
      window.location.href = "/register";
      return;
    }

    setLoading(true);
    try {
      const res = await apiFetch<{ url: string }>("/billing/create-checkout", {
        method: "POST",
      });
      window.location.href = res.url;
    } catch {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center text-2xl">
            You've used your 3 free searches
          </DialogTitle>
          <DialogDescription className="text-center">
            Upgrade to Pro for unlimited access.
          </DialogDescription>
        </DialogHeader>
        <div className="border rounded-lg p-6 mt-4">
          <p className="text-center text-3xl font-bold text-slate-900">
            $9.99<span className="text-base font-normal text-slate-500">/month</span>
          </p>
          <ul className="mt-4 space-y-2">
            {FEATURES.map((f) => (
              <li key={f} className="flex items-center gap-2 text-sm text-slate-700">
                <Check className="w-4 h-4 text-green-600" /> {f}
              </li>
            ))}
          </ul>
          <Button
            className="w-full mt-6"
            onClick={handleSubscribe}
            disabled={loading}
          >
            {!token
              ? "Create Account to Subscribe"
              : loading
                ? "Redirecting..."
                : "Subscribe Now"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
