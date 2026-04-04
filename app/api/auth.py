"""Authentication endpoints (placeholder for future implementation)."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
async def login():
    """
    Login endpoint - placeholder for future authentication.
    
    Will be implemented when auth system is added.
    """
    return {"message": "Authentication not implemented yet"}


@router.post("/logout")
async def logout():
    """
    Logout endpoint - placeholder for future authentication.
    
    Will be implemented when auth system is added.
    """
    return {"message": "Authentication not implemented yet"}
