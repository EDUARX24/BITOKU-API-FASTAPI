# Plan de Trabajo Frontend Next.js

Documento operativo para compartir con el equipo frontend o con otro modelo de IA. El objetivo es construir un frontend en Next.js consumiendo este backend FastAPI en desarrollo local.

## Contexto de integración

- Backend local: `http://localhost:8000`
- Frontend local esperado: `http://localhost:3000`
- En desarrollo (`ENV=dev`), la API acepta automáticamente requests desde `localhost` y `127.0.0.1` en cualquier puerto local
- Documentación del backend:
  - `http://localhost:8000/docs`
  - `http://localhost:8000/openapi.json`

## Contrato técnico que debe respetar el frontend

- Casi todos los endpoints devuelven `ApiResponse<T>`
- El payload útil viene en `result`
- Los errores se leen desde `errorMessages`
- La autenticación usa `Authorization: Bearer <token>`
- `GET /health` no usa `ApiResponse`
- `GET /api/ptn/pacientes/export` devuelve archivo Excel, no JSON
- Valores de dominio relevantes:
  - `rol`: `adm | doc | ptn`
  - `sexo`: `Masculino | Femenino | Otro`
  - `estado` de cita: `1 | 2 | 3`
- Regla importante de citas:
  - Si `estado = 3`, `motivocancalacion` es obligatorio
  - Si `estado != 3`, `motivocancalacion` debe ir vacío o ausente

## Archivos de referencia que el frontend debe usar

- `docs/FRONTEND_INTEGRATION_LOCAL.md`
- `docs/frontend-starter/nextjs/README.md`
- `docs/frontend-starter/nextjs/api.ts`
- `docs/frontend-starter/nextjs/types.ts`
- `docs/frontend-starter/nextjs/auth.ts`
- `docs/frontend-starter/nextjs/server-api.ts`
- `docs/frontend-starter/nextjs/app/login/page.tsx`
- `docs/frontend-starter/nextjs/app/login/actions.ts`
- `docs/frontend-starter/nextjs/app/servicios/page.tsx`

## Plan por fases

### Fase 1. Base del proyecto

Objetivo: dejar lista la base técnica del frontend.

Tareas:

- Crear proyecto Next.js con App Router y TypeScript
- Configurar `.env.local` con:
  - `NEXT_PUBLIC_API_URL=http://localhost:8000`
  - `API_URL=http://localhost:8000`
- Crear estructura base:
  - `src/app`
  - `src/lib`
  - `src/types`
- Copiar y adaptar los archivos starter:
  - `api.ts`
  - `auth.ts`
  - `types.ts`

Criterio de aceptación:

- El proyecto compila
- `GET /health` responde desde el frontend
- El cliente HTTP ya interpreta `ApiResponse<T>`

### Fase 2. Autenticación

Objetivo: permitir login y sesión básica.

Tareas:

- Implementar formulario de login usando `POST /api/auth/Login`
- Guardar token en cookie `httpOnly` en el servidor
- Crear helper para leer la sesión actual
- Redirigir a `/login` cuando no haya token en páginas protegidas
- Preparar logout

Criterio de aceptación:

- El usuario puede autenticarse
- El token se usa en requests protegidos
- Fallos de login muestran `errorMessages`

### Fase 3. Módulo de servicios

Objetivo: levantar el primer módulo real de negocio.

Tareas:

- Implementar listado de servicios con paginación básica
- Implementar crear servicio
- Implementar editar servicio
- Implementar eliminar servicio
- Mostrar estados de carga, vacío y error

Endpoints:

- `GET /api/servicios/servicios`
- `POST /api/servicios/servicios`
- `PATCH /api/servicios/servicios/{servicio_id}`
- `DELETE /api/servicios/servicios/{servicio_id}`

Criterio de aceptación:

- CRUD funcional desde el frontend
- Errores del backend visibles en UI

### Fase 4. Módulos base de catálogo

Objetivo: crear las pantallas base para usuarios clínicos.

Tareas:

- Pacientes:
  - listado
  - detalle
  - creación
  - edición
  - exportación
- Doctores:
  - listado
  - detalle
  - creación
  - edición
- Validar y normalizar visualmente los campos `sexo` y `rol`

Endpoints:

- Pacientes:
  - `POST /api/ptn/paciente`
  - `GET /api/ptn/pacientes`
  - `GET /api/ptn/paciente/{idPaciente}`
  - `PATCH /api/ptn/paciente/{idPaciente}`
  - `DELETE /api/ptn/paciente/{idPaciente}`
  - `GET /api/ptn/pacientes/export`
- Doctores:
  - `POST /api/doc/doctors`
  - `GET /api/doc/doctors`
  - `GET /api/doc/doctors/{idDoctor}`
  - `PATCH /api/doc/doctors/{idDoctor}`
  - `DELETE /api/doc/doctors/{idDoctor}`

Criterio de aceptación:

- Formularios y listados consumen la API real
- Exportación de pacientes descarga archivo correctamente

### Fase 5. Citas médicas

Objetivo: administrar citas con validaciones de dominio.

Tareas:

- Implementar listado general de citas
- Implementar citas por paciente
- Implementar creación, edición y cancelación
- En UI, cuando `estado = 3`, requerir `motivocancalacion`

Endpoints:

- `POST /api/cita/cita-medica`
- `GET /api/cita/citas-paciente`
- `GET /api/cita/citas-paciente/{id_paciente}`
- `PATCH /api/cita/cita-medica/{id_cita}`
- `DELETE /api/cita/cita-medica/{id_cita}`

Criterio de aceptación:

- La UI respeta la regla de cancelación
- No se envían payloads inválidos

### Fase 6. Consultas

Objetivo: completar el flujo clínico.

Tareas:

- Implementar listado de consultas
- Implementar detalle
- Implementar creación vinculada a cita y servicios
- Implementar edición

Endpoints:

- `POST /api/consulta/consulta`
- `GET /api/consulta/consultas`
- `GET /api/consulta/consulta/{id_consulta}`
- `PATCH /api/consulta/consulta/{id_consulta}`
- `DELETE /api/consulta/consulta/{id_consulta}`

Criterio de aceptación:

- Se puede crear una consulta con `servicios: number[]`
- El detalle muestra datos coherentes con la cita asociada

## Reglas de implementación para el frontend

- Centralizar todas las llamadas HTTP en un cliente único
- No consumir directamente `response.json()` en cada página
- Resolver el envelope `ApiResponse<T>` en `lib/api.ts`
- Mantener los tipos de dominio en `src/types`
- Usar Server Components o Route Handlers cuando tenga sentido para proteger token y reducir lógica cliente
- Los formularios deben mapear exactamente los nombres del backend
- Fechas deben enviarse en formato ISO compatible con FastAPI

## Orden recomendado de ejecución para un modelo de IA

1. Crear la estructura base del proyecto y variables de entorno
2. Copiar el starter de `docs/frontend-starter/nextjs`
3. Ajustar imports y rutas internas del proyecto Next.js
4. Implementar login y protección de rutas
5. Implementar módulo `servicios` como primera vertical completa
6. Continuar con `pacientes`, `doctores`, `citas` y `consultas`
7. Probar errores, estados vacíos y ausencia de token

## Prompt sugerido para otro modelo de IA

```text
Trabaja sobre un proyecto Next.js con App Router y TypeScript.

Objetivo: integrar este frontend con un backend FastAPI local disponible en http://localhost:8000.

Reglas del backend:
- Casi todos los endpoints responden con ApiResponse<T>
- El dato útil viene en result
- Los errores vienen en errorMessages
- La autenticación usa Authorization: Bearer <token>
- GET /health no usa ApiResponse
- GET /api/ptn/pacientes/export devuelve archivo

Usa como referencia estos archivos del backend:
- docs/FRONTEND_INTEGRATION_LOCAL.md
- docs/frontend-starter/nextjs/api.ts
- docs/frontend-starter/nextjs/types.ts
- docs/frontend-starter/nextjs/auth.ts
- docs/frontend-starter/nextjs/server-api.ts
- docs/frontend-starter/nextjs/app/login/page.tsx
- docs/frontend-starter/nextjs/app/login/actions.ts
- docs/frontend-starter/nextjs/app/servicios/page.tsx

Primero implementa autenticación y el módulo de servicios. Después continúa con pacientes, doctores, citas y consultas. Mantén un cliente HTTP centralizado, usa tipos estrictos y muestra errores del backend en la interfaz.
```
