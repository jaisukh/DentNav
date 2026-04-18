import { API_ROUTES } from "./routes";

/** OAuth entrypoint URL on backend; browser must navigate to it. */
export function getGoogleSignInUrl(): string {
  return API_ROUTES.googleLogin;
}
