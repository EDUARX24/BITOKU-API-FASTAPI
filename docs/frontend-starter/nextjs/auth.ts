import { cookies } from "next/headers";

const TOKEN_COOKIE = "bitoku_token";

export async function setAuthToken(token: string) {
  const cookieStore = await cookies();
  cookieStore.set(TOKEN_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: false,
    path: "/",
    maxAge: 60 * 60 * 24,
  });
}

export async function clearAuthToken() {
  const cookieStore = await cookies();
  cookieStore.delete(TOKEN_COOKIE);
}

export async function getAuthToken() {
  const cookieStore = await cookies();
  return cookieStore.get(TOKEN_COOKIE)?.value ?? null;
}
