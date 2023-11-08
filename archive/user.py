# class Gender(str, PyEnum):
#     male = "male"
#     female = "female"
#     non_binary = "non-binary"
#     transgender = "transgender"
#     genderqueer = "genderqueer"
#     two_spirit = "two-spirit"
#     bigender = "bigender"
#     pangender = "pangender"
#     agender = "agender"
#     demigender = "demigender"
#     third_gender = "third gender"
#     androgynous = "androgynous"
#     intersex = "intersex"
#     questioning = "questioning"
#     other = "other"


# @router.post("/users", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise internal_exceptions.EmailAlreadyRegisteredException()
#     return crud.create_user(db=db, user=user)


# @router.get("/users", response_model=List[schemas.User])
# def read_users(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users


# @router.get("/users/{user_id}", response_model=schemas.User)
# def read_user(
#     user_id: str,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     user = crud.get_user(db=db, user_id=user_id)
#     if user is None:
#         raise internal_exceptions.UserNotFoundException()
#     return user


# @router.put("/users/{user_id}", response_model=schemas.User)
# def update_user(
#     user_id: str,
#     user: schemas.UserUpdate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise internal_exceptions.UserNotFoundException()
#     return crud.update_user(db=db, db_user=db_user, user=user)


# def get_user_profile_image(db: Session, user_id: str):
#     db_user = db.query(models.User).filter(models.User.id == user_id).first()
#     return db_user.profile_image


# @router.get("/fetch-image")
# def fetch_image(url: str):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         mime_type = response.headers["content-type"]
#         base64_image = base64.b64encode(response.content).decode("utf-8")
#         return {"data_url": f"data:{mime_type};base64,{base64_image}"}
#     except requests.HTTPError as e:
#         raise HTTPException(status_code=400, detail="Image not found") from e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal server error") from e

# @router.post(
#     "/users/me/vaults/{vault_id}/share",
#     status_code=status.HTTP_204_NO_CONTENT,
#     tags=["current_user"]
# )
# def share_vault(
#     vault_id: str,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     peer_user_data = crud.get_user_by_email()
#     if not peer_user_data:
#         user = schemas.UserCreate(
#             id=user_id,
#             email=email,
#             first_name=first_name,
#             last_name=last_name
#         )
#         crud.create_user(db, user)
#     vault = crud.share_vault(db, vault_id=vault_id, peer_user_id=peer_user_id)
#     if vault is None:
#         raise HTTPException(status_code=404, detail="Vault not found")
#     return vault


# @router.get("/users/me", response_model=schemas.User, tags=["current_user"])
# def read_user_me(
#     current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
# ):
#     db_user = crud.get_user(db, user_id=current_user.id)
#     return db_user


# @router.get(
#     "/users/me/profile-image",
#     response_model=schemas.UserProfileImage,
#     tags=["current_user"],
# )
# def read_user_profile_image(
#     current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
# ):
#     image_binary_data = crud.get_user_profile_image(db, user_id=current_user.id)
#     if image_binary_data:
#         image_base64 = base64.b64encode(image_binary_data).decode("utf-8")
#     else:
#         image_base64 = None

#     user = schemas.UserProfileImage(profile_image=image_base64)
#     return user


# @router.put("/users/me", status_code=status.HTTP_204_NO_CONTENT, tags=["current_user"])
# async def update_user_me(
#     first_name: str = Form(...),
#     last_name: str = Form(...),
#     phone_no: str = Form(...),
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
#     file: UploadFile = File(None),
# ):
#     # Create UserUpdate schema
#     user_update = schemas.UserUpdate(
#         first_name=first_name, last_name=last_name, phone_no=phone_no
#     )

#     # Read the file
#     file_contents = None
#     if file:
#         file_contents = await file.read()
#         user_update.profile_image = file_contents

#     db_user = crud.get_user(db, user_id=current_user.id)
#     crud.update_user(db=db, db_user=db_user, user=user_update)


# @router.delete("/users/me/", status_code=status.HTTP_204_NO_CONTENT, tags=["user"])
# def delete_user_me(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return crud.delete_user(db=db, db_user=current_user)

# async def get_user_id(user_id: str = Header()):
#     return user_id