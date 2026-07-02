from pydantic import BaseModel

class CreateCategoryRequest(BaseModel):
    name:str
    description:str

class CategoryResponse(BaseModel):
    id:int
    name:str
    description:str

    class Config:
        from_attributes=True