"""
Simple explanation
- This file runs checks before requests reach endpoint handlers.
- It handles cross-cutting tasks like auth (login check).
- Think of it as a gatekeeper in front of routes.
"""

import os
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# HTTPBearer extracts the "Bearer <token>" header and passes it as credentials.
security = HTTPBearer()

async def verify_supabase_token(credentials: HTTPAuthorizationCredentials) -> str:
    """
    Validate a Supabase-issued JWT and return the user ID (sub claim).

    Supabase signs JWTs with ES256 (elliptic curve). We fetch the public keys
    from Supabase's JWKS endpoint at runtime so we never have to store the
    signing secret on the server — the public key is safe to fetch on demand.

    Returns:
        str: The authenticated user's UUID (the "sub" claim in the JWT).

    Raises:
        HTTPException 401: If the token is expired, invalid, or missing a user ID.
        HTTPException 500: If SUPABASE_URL is not configured.
    """
    try:
        token = credentials.credentials
        supabase_url = os.getenv("SUPABASE_URL")

        if not supabase_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase URL not configured",
            )

        # Fetch the public key from Supabase's JWKS endpoint
        jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )
        return user_id

    except jwt.ExpiredSignatureError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from error
    except jwt.InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {error!s}",
        ) from error

async def get_current_user_id(credentials: HTTPAuthorizationCredentials) -> str:
    """
    Thin wrapper used as a FastAPI Depends() dependency in every protected endpoint.
    Delegates to verify_supabase_token and returns the user ID string.
    """
    return await verify_supabase_token(credentials)