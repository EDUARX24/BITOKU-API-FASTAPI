# Next.js App Router Starter

Starter mínimo para consumir la API Bitoku desde un proyecto Next.js separado.

## Archivos

- `api.ts`: cliente HTTP tipado para la API
- `types.ts`: tipos de dominio y payloads
- `auth.ts`: manejo de token en cookie httpOnly
- `app/login/page.tsx`: formulario de login
- `app/login/actions.ts`: server actions para login/logout
- `app/servicios/page.tsx`: ejemplo real consumiendo `listServicios`

## Variables de entorno

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Uso sugerido

Copiar estos archivos al proyecto Next.js con una estructura parecida:

```text
src/
  app/
    layout.tsx
    page.tsx
    login/
      page.tsx
      actions.ts
    servicios/
      page.tsx
  lib/
    api.ts
    auth.ts
    types.ts
```

## Notas

- El login llama a `POST /api/auth/Login`
- El token se guarda en cookie `httpOnly`
- La página `/servicios` redirige a `/login` si no hay sesión
- El ejemplo usa Server Components + Server Actions

## Ajuste recomendado

En producción cambia `secure: false` por `secure: true` en `auth.ts`.
