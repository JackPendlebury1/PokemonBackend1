from typing import List, Optional, Any

from fastapi import Depends, FastAPI, HTTPException, status, Body, File, UploadFile, Form
from sqlalchemy.orm import Session
from . import crud, models, schemas, deps, security
from .database import SessionLocal, engine
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
import io
import base64
from io import BytesIO

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

##users

@app.get("/")
async def root():
    return {"msg" : "hii"}

##favourites

@app.post("/users/favourites/{favourite_index}")
async def create_movie_for_user(favourite_index: int, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)) -> Any:
    favourites = crud.get_favourites_by_index(db, favourite_index=favourite_index, owner_id=current_user.id)
    if favourites:
        raise HTTPException(status_code=400, detail="Pokemon Already Favourited")
    return crud.create_user_favourites(db=db, favourite_index=favourite_index, user_id=current_user.id)

@app.get("/favourites/{user_id}/",response_model=List[schemas.Favourites])
async def read_user_favourites(user_id: str, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)) -> Any:
    favourites = crud.get_user_favourites(db, user_id=user_id)
    return favourites

@app.get("/favourites/", response_model=List[schemas.Favourites])
async def read_favourites(db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)) -> Any:
    favourites = crud.get_favourites(db)
    return favourites

@app.post("/delete/favourites/{favourite_index}/")
async def delete_ticket_pnc(favourite_index : int, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)) -> Any:
    favourites = crud.delete_favourites(db, favourite_index, current_user.id)
    return favourites

##user

@app.post("/profile/image")
async def edit_user_image(image: UploadFile = File(...), db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)) -> Any:
    readImage = image.file.read()
    userImage = base64.encodestring(readImage)
    db_user = crud.update_image(db, email=current_user.email, userImage=userImage)
    return db_user

@app.post("/profile/edit", response_model=schemas.User)
async def edit_profile(user: schemas.UserUpdate, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)) -> Any:
    return crud.update_user(db=db, user=user, email=user.email)

@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)) -> Any:
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}/", response_model=schemas.User)
async def read_user(user_id: str, db: Session = Depends(deps.get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(db : Session = Depends(deps.get_db), form_data: deps.OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = security.timedelta(minutes=deps.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token,"token_type": "bearer"}


@app.get("/profile", response_model=schemas.User)
async def get_profile(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    return current_user

handler = Mangum(app)