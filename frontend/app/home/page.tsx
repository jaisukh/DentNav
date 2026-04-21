import { redirect } from "next/navigation";

/**
 * Legacy route from older OAuth docs that pointed `FRONTEND_BASE_URL` + `/home`.
 * Post-sign-in lives at `/landing`. Keep this as a redirect so misconfigured
 * redirects or bookmarks do not show a placeholder page.
 */
export default function HomeLegacyRedirectPage() {
  redirect("/landing");
}
