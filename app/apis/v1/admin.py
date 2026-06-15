from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.jwt import get_current_user
from app.core.db.databases import async_get_db
from app.models.users import User
from app.schemas.user import UserRead, UserRoleUpdate

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )
    return current_user


@router.get("/users", response_model=list[UserRead], summary="전체 회원 목록 조회")
async def get_users(
    query: str | None = Query(None, description="이름 또는 이메일 검색어"),
    department: str | None = Query(None, description="부서 필터"),
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(get_current_admin),
):
    stmt = select(User).order_by(User.id)

    if query:
        keyword = f"%{query}%"
        stmt = stmt.where(or_(User.name.like(keyword), User.email.like(keyword)))

    if department:
        stmt = stmt.where(User.department == department)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.patch("/users/role", response_model=UserRead, summary="회원 권한 변경")
async def update_user_role(
    role_in: UserRoleUpdate,
    db: AsyncSession = Depends(async_get_db),
    current_admin: User = Depends(get_current_admin),
):
    if role_in.user_id == current_admin.id and role_in.new_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 로그인한 관리자의 권한은 낮출 수 없습니다.",
        )

    result = await db.execute(select(User).where(User.id == role_in.user_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다.",
        )

    user.role = role_in.new_role
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
