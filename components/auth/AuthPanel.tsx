"use client";

import { useState } from "react";
import { LoginForm } from "@/components/auth/LoginForm";
import { SignupForm } from "@/components/auth/SignupForm";

export function AuthPanel() {
  const [mode, setMode] = useState<"login" | "signup">("login");

  return (
    <>
      <div className="space-y-1.5 text-center">
        {mode === "login" ? (
          <>
            <h2 className="font-display text-[22px] font-[800] leading-tight tracking-[-0.5px] text-[#0C1A3A] lg:text-[26px]">
              Welcome to DentNav 👋
            </h2>
            <p className="text-[16px] font-medium leading-[1.45] text-[#3E4850]">
              Sign in to access your personalized dental career roadmap
            </p>
          </>
        ) : (
          <>
            <h2 className="font-display text-[22px] font-[800] leading-tight tracking-[-0.5px] text-[#0C1A3A] lg:text-[26px]">
              Let&apos;s map what&apos;s next
            </h2>
            <p className="text-[16px] font-medium leading-[1.45] text-[#3E4850]">
              Your DentNav profile is the key — roadmap, resources, and community, synced in one place.
            </p>
          </>
        )}
      </div>

      {mode === "login" ? (
        <LoginForm onSignUp={() => setMode("signup")} />
      ) : (
        <SignupForm onSignIn={() => setMode("login")} />
      )}
    </>
  );
}
