from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, JSONResponse
from app.services.google_auth import get_oauth
from app.core.database import get_db
from app.models import User

router = APIRouter()

oauth = get_oauth()

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth", name="auth")
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to retrieve user info")

        email = user_info['email']
        user = db.query(User).filter(User.email == email).first()

        if not user:
            user = User(
                email=email,
                name=user_info.get("name"),
                picture=user_info.get("picture"),
                google_id=user_info.get("sub")
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        request.session['user'] = {
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }

        return RedirectResponse("http://localhost:3000/")  # Change to your frontend route
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": str(e)})

@router.get("/me")
def get_me(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in")
    return user
