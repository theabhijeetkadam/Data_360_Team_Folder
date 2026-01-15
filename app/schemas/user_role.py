from pydantic import BaseModel

class UserRoleBase(BaseModel):
    role_name: str

class UserRoleCreate(UserRoleBase):
    pass

class UserRole(UserRoleBase):
    role_id: int
    role_name: str

    class Config:
        from_attributes = True  # ✅ Correct for Pydantic v2