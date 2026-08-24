# Frontend architecture

The frontend uses a one-way dependency model:

```text
shared (api, components, hooks, lib, utils)
  -> features
    -> pages
      -> routes
        -> App
```

## Directory responsibilities

- `src/api`: transport primitives shared by multiple features. It must not contain feature state.
- `src/components`: reusable, business-agnostic UI and charts.
- `src/features/<feature>`: feature-owned API declarations, components, hooks, data, and transformations.
- `src/pages`: thin route entry points that compose a feature. Pages do not call HTTP APIs directly.
- `src/routes`: route configuration and route-level loading states.
- `src/utils` and `src/hooks`: only utilities and hooks reused by multiple features.

## Import rules

- A feature may import shared code, but may not import another feature directly.
- Shared code may not import from features, pages, or routes.
- Feature-internal imports use relative paths.
- Pages and routes may compose multiple features when required.
- Browser code never reads service credentials. External financial APIs are accessed through the backend.

ESLint enforces the important dependency boundaries.

## Data ownership

Each route loads only its own data through a feature hook. Global providers are reserved for genuinely global concerns such as theme, authentication, and localization.

## Tests

Pure business transformations are covered with Node's built-in test runner. Component and browser tests can be added independently when user interaction becomes more complex.
