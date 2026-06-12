# from pydantic import BaseModel
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from app.models.users import User
# from app.core.db.databases import async_get_db

# # 1. 입력 모델 정의
# class FindIdRequest(BaseModel):
#     last_name: str
#     middle_name: str
#     first_name: str
#     employee_number: str

# @router.post("/find-id")
# async def find_id(request: FindIdRequest, db: AsyncSession = Depends(async_get_db)):
#     # 2. 이름 조합 (DB의 name 필드와 형식을 일치시킵니다)
#     full_name = f"{request.last_name}{request.middle_name}{request.first_name}"
    
#     # 3. DB 조회
#     query = select(User).filter(
#         User.name == full_name,
#         User.employee_number == request.employee_number
#     )
#     result = await db.execute(query)
#     user = result.scalars().first()
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="입력하신 정보와 일치하는 사용자를 찾을 수 없습니다."
#         )
    
#     return {"email": user.email}