"use client";

import Link from "next/link";
import { useState, type ComponentPropsWithoutRef, type ReactNode } from "react";
import { AlreadySignedInModal } from "@/components/ui/AlreadySignedInModal";
import { useAuthStatus } from "@/lib/use-auth-status";

type LinkProps = ComponentPropsWithoutRef<typeof Link>;

type SignInLinkProps = Omit<LinkProps, "href"> & {
  /** Defaults to `/auth/login`. */
  href?: LinkProps["href"];
  children: ReactNode;
};

/**
 * Drop-in replacement for the static `<Link href="/auth/login">…</Link>`.
 *
 * - When the user is already signed in, intercepts the click and shows a
 *   centered "You're already signed in" modal instead of navigating.
 * - During the in-flight session check, falls back to the normal href so the
 *   button never feels frozen if the API is slow.
 */
export function SignInLink({
  href = "/auth/login",
  onClick,
  children,
  ...rest
}: SignInLinkProps) {
  const auth = useAuthStatus();
  const [open, setOpen] = useState(false);

  function handleClick(event: React.MouseEvent<HTMLAnchorElement>) {
    onClick?.(event);
    if (event.defaultPrevented) return;
    if (auth.ready && auth.signedIn) {
      event.preventDefault();
      setOpen(true);
    }
  }

  return (
    <>
      <Link href={href} onClick={handleClick} {...rest}>
        {children}
      </Link>
      <AlreadySignedInModal open={open} onClose={() => setOpen(false)} />
    </>
  );
}
