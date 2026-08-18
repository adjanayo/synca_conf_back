---
name: container-security
description: Use whenever writing or reviewing a Dockerfile, choosing a base image, building/publishing a container image, or configuring anything inside a container. Trigger on "Dockerfile," "base image," "build the image," "what should run as root," "image scanning," or any Docker work.
---

# Container & Image Security

## Base images

- Pin a specific version tag, never `:latest` — `python:3.12-slim`, not `python:latest`.
- Prefer `-slim` or `-alpine` variants over full images.

## Build

- **Multi-stage builds.** Build dependencies in a build stage; final stage copies only runtime artifacts.
- **Never bake secrets into a layer.** No `ARG`/`ENV` with real credentials. Secrets injected at runtime.
- **`.dockerignore` matters as much as `.gitignore`.**
- Copy dependency manifests and install **before** copying application code (layer-caching pattern).

## Runtime

- **Run as a non-root user.** `USER app`, not `USER root`.
- Expose only the port the process listens on.
- Set a `HEALTHCHECK` where meaningful.

## Scanning

- Before a Dockerfile is done, scan the built image (Trivy or Grype) and fix or consciously accept findings.
- Wire image scanning into CI so newly-disclosed CVEs get caught on next build.
