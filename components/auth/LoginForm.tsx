"use client";

import Link from "next/link";

type LoginFormProps = {
  onSignUp?: () => void;
};

export function LoginForm({ onSignUp }: LoginFormProps) {
  return (
    <>
      {/* Social Auth */}
      <button
        type="button"
        className="flex w-full items-center justify-center gap-2.5 rounded-full border border-[#BEC8D2] bg-white py-2.5 transition-all hover:bg-slate-50 active:scale-[0.98] lg:py-3"
      >
        <svg className="h-5 w-5" viewBox="0 0 24 24" aria-hidden>
          <path
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            fill="#4285F4"
          />
          <path
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            fill="#34A853"
          />
          <path
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
            fill="#FBBC05"
          />
          <path
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            fill="#EA4335"
          />
        </svg>
        <span className="text-sm font-bold text-[#0C1A3A]">Continue with Google</span>
      </button>

      {/* Divider */}
      <div className="relative flex items-center py-2 lg:py-2.5">
        <div className="flex-grow border-t border-[#BEC8D2]/30" />
        <span className="mx-4 text-[12px] font-bold uppercase tracking-[1.2px] text-[#6E7881]">
          OR LOGIN WITH EMAIL
        </span>
        <div className="flex-grow border-t border-[#BEC8D2]/30" />
      </div>

      <form className="space-y-3 lg:space-y-4" onSubmit={(e) => e.preventDefault()}>
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[#6E7881] lg:pl-4">
            <svg
              className="h-4 w-4 lg:h-5 lg:w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden
            >
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
              <polyline points="22,6 12,13 2,6" />
            </svg>
          </div>
          <input
            type="email"
            name="email"
            autoComplete="email"
            placeholder="Email Address"
            className="w-full rounded-xl border border-[#BEC8D2] bg-[#F8F9FF] py-2.5 pl-11 pr-3 text-sm font-medium text-[#3E4850] placeholder:text-[#6E7881]/60 transition-colors focus:border-[#0EA5E9] focus:outline-none lg:py-3 lg:pl-12 lg:pr-4"
          />
        </div>

        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[#6E7881] lg:pl-4">
            <svg
              className="h-4 w-4 lg:h-5 lg:w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden
            >
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0110 0v4" />
            </svg>
          </div>
          <input
            type="password"
            name="password"
            autoComplete="current-password"
            placeholder="Password"
            className="w-full rounded-xl border border-[#BEC8D2] bg-[#F8F9FF] py-2.5 pl-11 pr-11 text-sm font-medium text-[#3E4850] placeholder:text-[#6E7881]/60 transition-colors focus:border-[#0EA5E9] focus:outline-none lg:py-3 lg:pl-12 lg:pr-12"
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 flex items-center pr-3 text-[#6E7881] lg:pr-4"
            aria-label="Toggle password visibility"
          >
            <svg
              className="h-4 w-4 lg:h-5 lg:w-5"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              viewBox="0 0 24 24"
              aria-hidden
            >
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </button>
        </div>

        <div className="flex items-center justify-between py-0.5">
          <label className="group flex cursor-pointer items-center gap-2">
            <input
              type="checkbox"
              name="remember"
              className="h-4 w-4 rounded border-[#BEC8D2] text-[#0EA5E9] focus:ring-[#0EA5E9]"
            />
            <span className="text-[12px] font-[600] text-[#3E4850] transition-colors group-hover:text-[#0C1A3A]">
              Remember me
            </span>
          </label>
          <Link
            href="#"
            className="text-[12px] font-bold text-[#0EA5E9] transition-colors hover:text-[#0284C7]"
          >
            Forgot password?
          </Link>
        </div>

        <button
          type="submit"
          className="w-full rounded-full bg-[#0EA5E9] py-2.5 text-sm font-bold text-white shadow-[0_4px_16px_rgba(0,101,145,0.25)] transition-all hover:bg-[#0284C7] hover:shadow-[0_6px_20px_rgba(0,101,145,0.3)] active:scale-[0.98] lg:py-3"
        >
          Login
        </button>
      </form>

      <div className="flex flex-wrap justify-center gap-x-1.5 gap-y-1 text-center text-sm font-medium text-[#3E4850]">
        Don&apos;t have an account?
        {onSignUp ? (
          <button
            type="button"
            onClick={onSignUp}
            className="inline-flex items-center gap-1 font-bold text-[#0EA5E9] transition-colors hover:text-[#0284C7]"
          >
            Sign up
            <svg className="h-2 w-2" viewBox="0 0 12 12" fill="none" aria-hidden>
              <path
                d="M1 1L11 6L1 11"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        ) : (
          <Link
            href="#"
            className="inline-flex items-center gap-1 font-bold text-[#0EA5E9] transition-colors hover:text-[#0284C7]"
          >
            Sign up
            <svg className="h-2 w-2" viewBox="0 0 12 12" fill="none" aria-hidden>
              <path
                d="M1 1L11 6L1 11"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </Link>
        )}
      </div>
    </>
  );
}
