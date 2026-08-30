# Security Policy

## Supported Version

Security fixes are applied to the current `main` branch. No released version exists yet.

## Reporting a Vulnerability

Use GitHub's private vulnerability reporting for this repository. Do not open a public issue for a vulnerability that could expose bookmark data, local profile paths, credentials, or a way to modify browser data.

Include the affected component, reproduction steps using synthetic data, impact, and any proposed mitigation. Do not attach real bookmark exports, browser databases, profile files, usernames, or machine-specific paths.

## Security Boundaries

- Browser data access is read-only.
- The application never automates a browser user interface.
- The application performs no network requests.
- macOS security controls are detected and reported, never bypassed.
- Bookmark content is written only during an explicit export and is not included in logs or preferences.
