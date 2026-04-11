import { API_ROUTES } from "./routes";

export type GoogleSignInResponse = {
  ok: true;
  provider: "google";
  message: string;
};

export async function signInWithGoogle(): Promise<GoogleSignInResponse> {
  const res = await fetch(API_ROUTES.authGoogle, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  if (!res.ok) throw new Error(`Sign-in request failed: ${res.status}`);
  return res.json() as Promise<GoogleSignInResponse>;
}
