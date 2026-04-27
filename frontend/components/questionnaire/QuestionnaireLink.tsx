"use client";

import Link from "next/link";
import { useState, type ComponentPropsWithoutRef, type ReactNode } from "react";
import { QuestionnaireDoneModal } from "@/components/ui/QuestionnaireDoneModal";
import { useAuthStatus } from "@/lib/use-auth-status";

type LinkProps = ComponentPropsWithoutRef<typeof Link>;

type QuestionnaireLinkProps = Omit<LinkProps, "href"> & {
  /** Defaults to `/questionnaire`. */
  href?: LinkProps["href"];
  children: ReactNode;
};

/**
 * Wraps `<Link href="/questionnaire">` so that signed-in users with an
 * existing analysis see the "you already have an analysis" modal in place
 * instead of being taken to the form. Clicking the modal's X stays put.
 *
 * Anonymous and signed-in-without-analysis users navigate as usual.
 */
export function QuestionnaireLink({
  href = "/questionnaire",
  onClick,
  children,
  ...rest
}: QuestionnaireLinkProps) {
  const auth = useAuthStatus();
  const [open, setOpen] = useState(false);

  function handleClick(event: React.MouseEvent<HTMLAnchorElement>) {
    onClick?.(event);
    if (event.defaultPrevented) return;
    if (auth.ready && auth.signedIn && auth.hasAnsweredQuestionnaire) {
      event.preventDefault();
      setOpen(true);
    }
  }

  return (
    <>
      <Link href={href} onClick={handleClick} {...rest}>
        {children}
      </Link>
      <QuestionnaireDoneModal open={open} onClose={() => setOpen(false)} />
    </>
  );
}
