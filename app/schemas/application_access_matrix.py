from pydantic import BaseModel

class ApplicationAccessMatrixBase(BaseModel):
    role_name: str
    sub_functionality_name: str
    action_type: str
    action_flag: bool

class ApplicationAccessMatrixCreate(ApplicationAccessMatrixBase):
    pass

class ApplicationAccessMatrixUpdate(ApplicationAccessMatrixBase):
    pass

class ApplicationAccessMatrixOut(ApplicationAccessMatrixBase):
    id: int

    class Config:
        from_attributes = True  # for Pydantic v2
