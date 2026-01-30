"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useUserStore } from "@/lib/store";

export default function Home() {
  const router = useRouter();
  const { email, diagnosticCompleted } = useUserStore();

  useEffect(() => {
    // Route based on user state:
    // - If no email and no diagnostic: show landing page
    // - If email captured or diagnostic done: go to dashboard
    if (email || diagnosticCompleted) {
      router.replace("/dashboard");
    } else {
      router.replace("/landing");
    }
  }, [email, diagnosticCompleted, router]);

  // Show loading state while determining route
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-fire-red border-t-transparent rounded-full animate-spin" />
    </div>
  );
}
