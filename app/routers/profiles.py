from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, EmailStr, constr, validator
from typing import List, Optional, Dict
from fastapi.responses import JSONResponse

router = APIRouter()

# In-memory storage (profile_id: profile_data)
profiles_db: Dict[int, dict] = {}
next_profile_id = 1

def email_exists(email: str, exclude_profile_id: Optional[int] = None) -> bool:
    for pid, profile in profiles_db.items():
        if profile["email"].lower() == email.lower():
            if exclude_profile_id is None or pid != exclude_profile_id:
                return True
    return False

class ProfileBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=50)
    email: EmailStr
    bio: constr(strip_whitespace=True, min_length=1, max_length=200)

    @validator("bio")
    def bio_max_length(cls, v):
        if len(v) > 200:
            raise ValueError("Bio must be at most 200 characters")
        return v

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None
    email: Optional[EmailStr] = None
    bio: Optional[constr(strip_whitespace=True, min_length=1, max_length=200)] = None

    @validator("bio")
    def bio_max_length(cls, v):
        if v and len(v) > 200:
            raise ValueError("Bio must be at most 200 characters")
        return v

class ProfileOut(ProfileBase):
    id: int

# Error response model
class ErrorResponse(BaseModel):
    detail: str

@router.post("/", response_model=ProfileOut, responses={400: {"model": ErrorResponse}}, status_code=201, summary="Create a new user profile")
def create_profile(profile: ProfileCreate):
    global next_profile_id
    if email_exists(profile.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address must be unique."
        )
    profile_id = next_profile_id
    next_profile_id += 1
    data = profile.dict()
    profiles_db[profile_id] = data.copy()
    return ProfileOut(id=profile_id, **data)

@router.get("/{profile_id}", response_model=ProfileOut, responses={404: {"model": ErrorResponse}}, summary="Get a user profile by ID")
def get_profile(profile_id: int):
    profile_data = profiles_db.get(profile_id)
    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found."
        )
    return ProfileOut(id=profile_id, **profile_data)

@router.patch("/{profile_id}", response_model=ProfileOut, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}, summary="Update a user profile (partial update)")
def update_profile(profile_id: int, payload: ProfileUpdate = Body(...)):
    existing = profiles_db.get(profile_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found."
        )
    update_data = payload.dict(exclude_unset=True)
    # Enforce unique email
    new_email = update_data.get("email")
    if new_email:
        if email_exists(new_email, exclude_profile_id=profile_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address must be unique."
            )
    # Validate length for bio (redundant due to Pydantic, but double-check)
    if "bio" in update_data and update_data["bio"] and len(update_data["bio"]) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bio must be at most 200 characters."
        )
    # Update fields
    existing.update(update_data)
    return ProfileOut(id=profile_id, **existing)
