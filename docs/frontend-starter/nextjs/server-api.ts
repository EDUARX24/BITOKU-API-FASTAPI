import { getAuthToken } from "./auth";
import {
  getHealth,
  listServicios,
  login,
} from "./api";
import type { LoginPayload } from "./types";

export async function loginAndStoreToken(
  payload: LoginPayload,
  setToken: (token: string) => Promise<void>
) {
  const result = await login(payload);
  await setToken(result.token);
  return result;
}

export async function getServiciosForCurrentSession() {
  const token = await getAuthToken();
  if (!token) {
    throw new Error("No authenticated session");
  }
  return listServicios(token);
}

export async function getHealthStatus() {
  return getHealth();
}
