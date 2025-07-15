Guide to the Project

This project involves adding user profile management functionality to an existing FastAPI application for a social networking platform. Your task is to expand and improve the backend by implementing endpoints dedicated to creating, retrieving, and updating user profiles. These operations should be managed through a dedicated router and must adhere to robust validation, modularity, and error handling standards.

Requirements:
- Implement an APIRouter for all profile-related endpoints under '/profiles'.
- Create endpoints for creating, fetching by ID, and updating profiles, ensuring:
  - Pydantic models are used for request/response, with custom validations.
  - Emails are unique across all profiles.
  - Bios do not exceed 200 characters.
- Use in-memory storage (such as a dict or list) for profile data.
- Ensure all error responses are structured with a 'detail' field and utilize FastAPI exception handling.
- Tag all endpoints properly for OpenAPI documentation.

Verifying Your Solution:
- The API should allow the creation of profiles with validated and unique data.
- Attempts to create or update profiles with duplicate emails or oversized bios should result in descriptive error responses.
- Retrieving or updating a non-existing profile should produce a 404 error with a 'detail' field.
- Partial updates via PATCH should be supported.
- All endpoints should be grouped under a '/profiles' path and properly tagged in the API documentation.
- Tests are included to verify compliance, error cases, and expected behaviors.

Focus on adhering to the requirements for validation, modularity, and clear, maintainable code. Avoid implementing unrelated features such as authentication or database integration.