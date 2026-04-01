from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import verify_access_token
from backend.db.session import get_db
from backend.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
	token: str = Depends(oauth2_scheme),
	db: AsyncSession = Depends(get_db),
):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	payload = verify_access_token(token)
	if not payload:
		raise credentials_exception

	sub = payload.get("sub")
	if not sub:
		raise credentials_exception

	try:
		user_id = int(sub)
	except ValueError:
		raise credentials_exception

	result = await db.execute(select(User).where(User.id == user_id))
	user = result.scalars().first()
	if not user:
		raise credentials_exception

	if not user.is_active:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Inactive user cannot access this resource",
		)

	return user
