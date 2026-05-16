"use client";

import { Suspense } from "react";
import { LoginForm } from "@/components/auth/LoginForm";

export function AuthPanel() {
  return (
    <div className="flex min-h-0 w-full flex-col gap-8 lg:gap-10">
      <div className="space-y-2 text-center lg:space-y-3">
        <h2 className="font-display text-[24px] font-[800] leading-tight tracking-[-0.5px] text-[#0C1A3A] lg:text-[28px]">
          Welcome to DentNav
        </h2>
        <p className="mx-auto max-w-[340px] text-[15px] font-medium leading-[1.5] text-[#3E4850] lg:max-w-none lg:text-[16px] lg:leading-relaxed">
          Sign in with Google to access your personalized dental career roadmap,
          resources, and community.
        </p>
      </div>

      <Suspense>
        <LoginForm />
      </Suspense>
    </div>
  );
}
