# Frontend Integration Guide

Guía de consumo local de la API Bitoku desde un proyecto frontend separado, por ejemplo Next.js.

## Objetivo

Este archivo está pensado para ser compartido con el proyecto frontend. Describe:

- cómo correr el backend localmente
- cómo consumirlo desde Next.js
- formato real de respuestas
- autenticación
- rutas disponibles
- convenciones de dominio que el frontend debe respetar

## Backend local

Ejecutar el backend desde este proyecto:

```powershell
env\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Base URL local:

```text
http://localhost:8000
```

Healthcheck:

```text
GET http://localhost:8000/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "environment": "dev",
  "version": "1.0.0"
}
```

## CORS

Para desarrollo con Next.js local, el backend debe tener en `.env` algo como:

```env
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

Si el frontend corre en otra máquina o en otro puerto, agrega ese origen.

En desarrollo (`ENV=dev`), el backend también acepta automáticamente estos orígenes locales:

```text
http://localhost:<puerto>
http://127.0.0.1:<puerto>
```

Eso permite consumir la API desde otro proyecto Next.js local sin depender estrictamente de `BACKEND_CORS_ORIGINS` para cada puerto. Si el frontend corre fuera de `localhost` o `127.0.0.1`, sí debes declararlo explícitamente en `BACKEND_CORS_ORIGINS`.

## Frontend local

En el proyecto Next.js:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Si usas acciones del servidor o route handlers en Next.js, también puedes usar:

```env
API_URL=http://localhost:8000
```

Si `ENABLE_DOCS=true`, puedes inspeccionar el contrato real del backend en:

```text
http://localhost:8000/docs
http://localhost:8000/openapi.json
```

## Formato de respuestas

### Respuestas normales

Casi todos los endpoints devuelven este envelope:

```json
{
  "statusCode": 200,
  "isSuccess": true,
  "errorMessages": [],
  "successMessages": [],
  "result": {}
}
```

Convención:

- `statusCode`: código lógico y también coincide con el HTTP status
- `isSuccess`: `true` o `false`
- `errorMessages`: arreglo de mensajes de error
- `successMessages`: arreglo de mensajes de éxito
- `result`: payload real

### Excepciones

Los errores también salen envueltos:

```json
{
  "statusCode": 404,
  "isSuccess": false,
  "errorMessages": ["Servicio no encontrado"],
  "successMessages": [],
  "result": null
}
```

### Excepciones a esta regla

- `GET /health` no usa `ApiResponse`
- `GET /api/ptn/pacientes/export` devuelve un archivo Excel

## Autenticación

La API usa Bearer Token.

### Registro

```text
POST /api/auth/Register
```

Body:

```json
{
  "nombreUsuario": "admin_demo",
  "contrasenia": "Secret123!",
  "rol": "adm"
}
```

Roles válidos:

- `adm`
- `doc`
- `ptn`

También acepta aliases y los normaliza:

- `admin` -> `adm`
- `doctor` -> `doc`
- `paciente` -> `ptn`

### Login

```text
POST /api/auth/Login
```

Body:

```json
{
  "username": "admin_demo",
  "password": "Secret123!"
}
```

Respuesta:

```json
{
  "statusCode": 200,
  "isSuccess": true,
  "errorMessages": [],
  "successMessages": [],
  "result": {
    "user": {
      "idUsuario": 1,
      "nombreUsuario": "admin_demo",
      "rol": "adm"
    },
    "token": "..."
  }
}
```

### Header requerido

```http
Authorization: Bearer <token>
```

## Convenciones de dominio importantes

### Sexo

Valores canónicos:

- `Masculino`
- `Femenino`
- `Otro`

El backend también acepta aliases como:

- `M`
- `F`
- `male`
- `female`
- `masculino`
- `femenino`

Pero el frontend debería enviar preferiblemente los valores canónicos.

### Estado de cita

Valores válidos:

- `1`: programada
- `2`: completada
- `3`: cancelada

Regla:

- si `estado = 3`, `motivocancalacion` es obligatorio
- si `estado != 3`, `motivocancalacion` debe ir vacío o ausente

## Rutas disponibles

## Health

- `GET /health`

## Auth

Prefijo real:

```text
/api/auth
```

Rutas:

- `POST /api/auth/Register`
- `POST /api/auth/Login`
- `GET /api/auth/List`

## Paciente

Prefijo real:

```text
/api/ptn
```

Rutas:

- `POST /api/ptn/paciente`
- `GET /api/ptn/pacientes`
- `GET /api/ptn/paciente/{idPaciente}`
- `PUT /api/ptn/paciente/{idPaciente}`
- `PATCH /api/ptn/paciente/{idPaciente}`
- `DELETE /api/ptn/paciente/{idPaciente}`
- `GET /api/ptn/pacientes/export`

## Doctor

Prefijo real:

```text
/api/doc
```

Rutas:

- `POST /api/doc/doctors`
- `GET /api/doc/doctors`
- `GET /api/doc/doctors/{idDoctor}`
- `PUT /api/doc/doctors/{idDoctor}`
- `PATCH /api/doc/doctors/{idDoctor}`
- `DELETE /api/doc/doctors/{idDoctor}`

## Citas médicas

Prefijo real:

```text
/api/cita
```

Rutas:

- `POST /api/cita/cita-medica`
- `GET /api/cita/citas-paciente`
- `GET /api/cita/citas-paciente/{id_paciente}`
- `PUT /api/cita/cita-medica/{id_cita}`
- `PATCH /api/cita/cita-medica/{id_cita}`
- `DELETE /api/cita/cita-medica/{id_cita}`

## Servicios

Prefijo real:

```text
/api/servicios
```

Rutas:

- `POST /api/servicios/servicios`
- `GET /api/servicios/servicios`
- `GET /api/servicios/servicios/{servicio_id}`
- `PATCH /api/servicios/servicios/{servicio_id}`
- `DELETE /api/servicios/servicios/{servicio_id}`

## Consulta

Prefijo real:

```text
/api/consulta
```

Rutas:

- `POST /api/consulta/consulta`
- `GET /api/consulta/consultas`
- `GET /api/consulta/consulta/{id_consulta}`
- `PUT /api/consulta/consulta/{id_consulta}`
- `PATCH /api/consulta/consulta/{id_consulta}`
- `DELETE /api/consulta/consulta/{id_consulta}`

## Recomendación para el frontend

Crear un cliente HTTP centralizado que:

- inyecte `Authorization` cuando exista token
- lea `isSuccess`
- lance errores usando `errorMessages`
- retorne directamente `result`

Ejemplo con `fetch`:

```ts
const API_URL = process.env.NEXT_PUBLIC_API_URL!;

type ApiResponse<T> = {
  statusCode: number;
  isSuccess: boolean;
  errorMessages: string[];
  successMessages: string[];
  result: T;
};

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  token?: string
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  const data = (await response.json()) as ApiResponse<T>;

  if (!response.ok || !data.isSuccess) {
    throw new Error(data.errorMessages?.join(", ") || "API error");
  }

  return data.result;
}
```

Ejemplos:

```ts
export function login(username: string, password: string) {
  return apiFetch<{ user: { idUsuario: number; nombreUsuario: string; rol: string }; token: string }>(
    "/api/auth/Login",
    {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }
  );
}

export function getServicios(token: string) {
  return apiFetch<any[]>(
    "/api/servicios/servicios?pageSize=20&pageNumber=1",
    { method: "GET" },
    token
  );
}
```

## Recomendación de estructura en Next.js

- `src/lib/api.ts`
- `src/lib/auth.ts`
- `src/types/api.ts`
- `src/types/domain.ts`

En este repo ya existe un starter portable listo para copiar al frontend:

- [api.ts](C:/Users/Eduar%20Garcia/Documents/Bitoku-FastApi/docs/frontend-starter/nextjs/api.ts)
- [types.ts](C:/Users/Eduar%20Garcia/Documents/Bitoku-FastApi/docs/frontend-starter/nextjs/types.ts)
- [auth.ts](C:/Users/Eduar%20Garcia/Documents/Bitoku-FastApi/docs/frontend-starter/nextjs/auth.ts)
- [README.md](C:/Users/Eduar%20Garcia/Documents/Bitoku-FastApi/docs/frontend-starter/nextjs/README.md)
- ejemplo App Router:
  [layout.tsx](C:/Users/Eduar%20Garcia/Documents/Bitoku-FastApi/docs/frontend-starter/nextjs/app/layout.tsx)
  [login/page.tsx](C:/Users/Eduar%20Garcia/Documents/Bitoku-FastApi/docs/frontend-starter/nextjs/app/login/page.tsx)
  [login/actions.ts](C:/Users/Eduar%20Garcia/Documents/Bitoku-FastApi/docs/frontend-starter/nextjs/app/login/actions.ts)
  [servicios/page.tsx](C:/Users/Eduar%20Garcia/Documents/Bitoku-FastApi/docs/frontend-starter/nextjs/app/servicios/page.tsx)

Tipos mínimos sugeridos:

```ts
export type Role = "adm" | "doc" | "ptn";
export type Sex = "Masculino" | "Femenino" | "Otro";
export type AppointmentStatus = 1 | 2 | 3;
```

## Sugerencia para el modelo del frontend

Si este archivo se comparte con otro proyecto o con un modelo, asumir siempre:

- la API corre en `NEXT_PUBLIC_API_URL`
- casi todos los endpoints usan `ApiResponse`
- el payload útil siempre viene en `result`
- el token se envía por `Authorization: Bearer <token>`
- `sexo`, `rol` y `estado` deben respetar los valores descritos arriba
- `GET /health` no usa `ApiResponse`
- `GET /api/ptn/pacientes/export` devuelve un archivo, no JSON
