/**
 * Sign-in entry. Currently sends users straight to the signed-in shell.
 * When wiring real Google OAuth, switch this to `API_ROUTES.googleLogin`.
 */
export function getGoogleSignInUrl(): string {
  return "/landing";
}
