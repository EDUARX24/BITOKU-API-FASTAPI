import type {
  ApiResponse,
  CitaMedica,
  Consulta,
  CreateCitaPayload,
  CreateConsultaPayload,
  CreateDoctorPayload,
  CreatePacientePayload,
  CreateServicioPayload,
  Doctor,
  LoginPayload,
  LoginResult,
  Paciente,
  RegisterPayload,
  Servicio,
  UpdateCitaPayload,
  UpdateConsultaPayload,
  UpdateDoctorPayload,
  UpdatePacientePayload,
  UpdateServicioPayload,
  Usuario,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type RequestOptions = RequestInit & {
  token?: string;
};

async function parseResponse<T>(response: Response): Promise<T> {
  const data = (await response.json()) as ApiResponse<T>;

  if (!response.ok || !data.isSuccess) {
    const message =
      data.errorMessages?.join(", ") ||
      `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return data.result;
}

export async function apiFetch<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { token, headers, ...rest } = options;
  const finalHeaders = new Headers(headers);

  if (!finalHeaders.has("Content-Type") && rest.body) {
    finalHeaders.set("Content-Type", "application/json");
  }

  if (token) {
    finalHeaders.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: finalHeaders,
    cache: "no-store",
  });

  return parseResponse<T>(response);
}

export async function getHealth() {
  const response = await fetch(`${API_URL}/health`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Healthcheck failed with status ${response.status}`);
  }
  return response.json() as Promise<{
    status: string;
    environment: string;
    version: string;
  }>;
}

export function registerUser(payload: RegisterPayload) {
  return apiFetch<Usuario>("/api/auth/Register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function login(payload: LoginPayload) {
  return apiFetch<LoginResult>("/api/auth/Login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listUsers(token: string, pageSize = 20, pageNumber = 1) {
  return apiFetch<Usuario[]>(
    `/api/auth/List?pageSize=${pageSize}&pageNumber=${pageNumber}`,
    { method: "GET", token }
  );
}

export function createPaciente(token: string, payload: CreatePacientePayload) {
  return apiFetch<Paciente>("/api/ptn/paciente", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function listPacientes(token: string, pageSize = 20, pageNumber = 1) {
  return apiFetch<Paciente[]>(
    `/api/ptn/pacientes?pageSize=${pageSize}&pageNumber=${pageNumber}`,
    { method: "GET", token }
  );
}

export function getPaciente(token: string, idPaciente: number) {
  return apiFetch<Paciente>(`/api/ptn/paciente/${idPaciente}`, {
    method: "GET",
    token,
  });
}

export function updatePaciente(
  token: string,
  idPaciente: number,
  payload: UpdatePacientePayload
) {
  return apiFetch<Paciente>(`/api/ptn/paciente/${idPaciente}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
    token,
  });
}

export function deletePaciente(token: string, idPaciente: number) {
  return apiFetch<Paciente>(`/api/ptn/paciente/${idPaciente}`, {
    method: "DELETE",
    token,
  });
}

export function createDoctor(token: string, payload: CreateDoctorPayload) {
  return apiFetch<Doctor>("/api/doc/doctors", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function listDoctors(token: string, pageSize = 20, pageNumber = 1) {
  return apiFetch<Doctor[]>(
    `/api/doc/doctors?pageSize=${pageSize}&pageNumber=${pageNumber}`,
    { method: "GET", token }
  );
}

export function getDoctor(token: string, idDoctor: number) {
  return apiFetch<Doctor>(`/api/doc/doctors/${idDoctor}`, {
    method: "GET",
    token,
  });
}

export function updateDoctor(
  token: string,
  idDoctor: number,
  payload: UpdateDoctorPayload
) {
  return apiFetch<Doctor>(`/api/doc/doctors/${idDoctor}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
    token,
  });
}

export function deleteDoctor(token: string, idDoctor: number) {
  return apiFetch<Doctor>(`/api/doc/doctors/${idDoctor}`, {
    method: "DELETE",
    token,
  });
}

export function createServicio(token: string, payload: CreateServicioPayload) {
  return apiFetch<Servicio>("/api/servicios/servicios", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function listServicios(token: string, pageSize = 20, pageNumber = 1) {
  return apiFetch<Servicio[]>(
    `/api/servicios/servicios?pageSize=${pageSize}&pageNumber=${pageNumber}`,
    { method: "GET", token }
  );
}

export function getServicio(token: string, servicioId: number) {
  return apiFetch<Servicio>(`/api/servicios/servicios/${servicioId}`, {
    method: "GET",
    token,
  });
}

export function updateServicio(
  token: string,
  servicioId: number,
  payload: UpdateServicioPayload
) {
  return apiFetch<Servicio>(`/api/servicios/servicios/${servicioId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
    token,
  });
}

export function deleteServicio(token: string, servicioId: number) {
  return apiFetch<null>(`/api/servicios/servicios/${servicioId}`, {
    method: "DELETE",
    token,
  });
}

export function createCita(token: string, payload: CreateCitaPayload) {
  return apiFetch<CitaMedica>("/api/cita/cita-medica", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function listCitas(token: string, pageSize = 20, pageNumber = 1) {
  return apiFetch<CitaMedica[]>(
    `/api/cita/citas-paciente?pageSize=${pageSize}&pageNumber=${pageNumber}`,
    { method: "GET", token }
  );
}

export function listCitasByPaciente(token: string, pacienteId: number) {
  return apiFetch<CitaMedica[]>(`/api/cita/citas-paciente/${pacienteId}`, {
    method: "GET",
    token,
  });
}

export function updateCita(
  token: string,
  citaId: number,
  payload: UpdateCitaPayload
) {
  return apiFetch<CitaMedica>(`/api/cita/cita-medica/${citaId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
    token,
  });
}

export function deleteCita(token: string, citaId: number) {
  return apiFetch<CitaMedica>(`/api/cita/cita-medica/${citaId}`, {
    method: "DELETE",
    token,
  });
}

export function createConsulta(token: string, payload: CreateConsultaPayload) {
  return apiFetch<Consulta>("/api/consulta/consulta", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function listConsultas(token: string, pageSize = 20, pageNumber = 1) {
  return apiFetch<Consulta[]>(
    `/api/consulta/consultas?pageSize=${pageSize}&pageNumber=${pageNumber}`,
    { method: "GET", token }
  );
}

export function getConsulta(token: string, consultaId: number) {
  return apiFetch<Consulta>(`/api/consulta/consulta/${consultaId}`, {
    method: "GET",
    token,
  });
}

export function updateConsulta(
  token: string,
  consultaId: number,
  payload: UpdateConsultaPayload
) {
  return apiFetch<Consulta>(`/api/consulta/consulta/${consultaId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
    token,
  });
}

export function deleteConsulta(token: string, consultaId: number) {
  return apiFetch<Consulta>(`/api/consulta/consulta/${consultaId}`, {
    method: "DELETE",
    token,
  });
}
