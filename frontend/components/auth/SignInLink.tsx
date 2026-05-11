"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type ComponentPropsWithoutRef, type ReactNode } from "react";
import { useAuthStatus } from "@/lib/auth-status-context";

type LinkProps = ComponentPropsWithoutRef<typeof Link>;

type SignInLinkProps = Omit<LinkProps, "href"> & {
  /** Defaults to `/auth/login`. */
  href?: LinkProps["href"];
  children: ReactNode;
};

/**
 * Drop-in replacement for `<Link href="/auth/login">`.
 * When the user is already signed in, sends them directly to /landing
 * instead of navigating to the login page.
 */
export function SignInLink({
  href = "/auth/login",
  onClick,
  children,
  ...rest
}: SignInLinkProps) {
  const auth = useAuthStatus();
  const router = useRouter();

  function handleClick(event: React.MouseEvent<HTMLAnchorElement>) {
    onClick?.(event);
    if (event.defaultPrevented) return;
    if (auth.ready && auth.signedIn) {
      event.preventDefault();
      router.push("/landing");
    }
  }

  return (
    <Link href={href} onClick={handleClick} {...rest}>
      {children}
    </Link>
  );
}
