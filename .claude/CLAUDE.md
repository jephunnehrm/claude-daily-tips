\# Python Standards



\## Architecture

\- Modular structure (services, models, routes)

\- Separate business logic from API layer



\---



\## Code Style

\- Use type hints everywhere

\- Prefer dataclasses or pydantic models

\- Follow PEP8 standards



\---



\## Frameworks

\- Keep framework code thin (FastAPI / Flask)

\- Business logic should be framework-agnostic



\---



\## Error Handling

\- Use structured error responses

\- Avoid generic exception swallowing



\---



\## Testing

\- Use pytest

\- Test business logic, not framework glue code



\---



\## Data Handling

\- Validate inputs using schema models

\- Avoid untyped dictionaries in core logic

