from fastapi import Request, Depends, APIRouter,HTTPException,status
from fastapi.responses import RedirectResponse
import logging
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
# from app.database import get_db  # your db session getter
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.models import User 

logger = logging.getLogger("uvicorn")
router = APIRouter()

oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')  
    print(redirect_uri)
    # callback URL
    return await oauth.google.authorize_redirect(request, redirect_uri)
# @router.get("/test")
# async def test_session(request: Request):
#     # logger.info("suman was here!");  
#     request.session["foo"] = "bar"
#     return {"message": request.session.get("foo")}
@router.get("/auth", name="auth") 
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        # Get the OAuth token after redirect
        token = await oauth.google.authorize_access_token(request)
        
        # Extract user info from token
        user_info = token.get("userinfo")
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        email = user_info['email']
        google_id = user_info['sub']
        name = user_info.get('name')
        picture = user_info.get('picture')

        # Check if user exists in DB
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Create new user if doesn't exist
            user = User(email=email, name=name, picture=picture, google_id=google_id)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Set user info into session
        request.session['user'] = {
            'email': user.email,
            'name': user.name,
            'picture': user.picture
        }

        # Redirect user after successful login
        return RedirectResponse(url="/")

    except Exception as e:
        import traceback
        traceback.print_exc()  # Log full error for debugging
        return JSONResponse(status_code=500, content={"detail": str(e)})

    try:
        token = await oauth.google.authorize_access_token(request)
        # print(token.userinfo.email)
        user_info = token.get("userinfo")
        print(user_info)
# Method 2: Direct access (make sure it's guaranteed to exist or wrap in try-except)
# id_token = token["id_token"]

        print("🆔 ID Token:", user_info)
        # user_info = await oauth.google.parse_id_token(request, token)
        print(user_info,'SU')
        email = user_info['email']
        google_id = user_info['sub']
        name = user_info.get('name')
        picture = user_info.get('picture')

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name=name, picture=picture, google_id=google_id)
            db.add(user)
            db.commit()
            db.refresh(user)

        request.session['user'] = {
            'email': user.email,
            'name': user.name,
            'picture': user.picture
        }

        return RedirectResponse(url="/")
    
    except Exception as e:
        import traceback
        traceback.print_exc()  # prints full error in terminal
        return JSONResponse(status_code=500, content={"detail": str(e)})