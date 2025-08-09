from fastapi import FastAPI, Request,Depends,Form,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from .import models
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.db import SessionLocal, engine
from app.models import Base, SheetData
from app.utils.sheet import get_sheet_data
from sqlalchemy.orm import Session



SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

ALLOWED_EMAILS = ["admin@example.com", "manager@example.com"]


app = FastAPI()
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=302, detail="Not logged in", headers={"Location": "/login"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None or email not in ALLOWED_EMAILS:
            raise HTTPException(status_code=302, headers={"Location": "/login"})
        return email
    except JWTError:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})

@app.post("/login", response_class=HTMLResponse)
def login(email: str = Form(...)):
    if email not in ALLOWED_EMAILS:
        return templates.TemplateResponse("login.html", {"request": {}, "error": "Access denied!"})

    access_token = create_access_token(data={"sub": email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=1800)
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response




@app.post("/import-sheet")
def import_sheet(db: Session = Depends(get_db)):
    sheet_data = get_sheet_data("Sample form responses")

    inserted = 0
    for row in sheet_data:
        record = SheetData(**row)
        db.merge(record) 
        inserted += 1

    db.commit()
    return RedirectResponse(
        url=f"/dashboard?message={inserted}+rows+imported+successfully!", 
        status_code=303
    )

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(
    request: Request, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user),
    message: str = "", 
    show: str = "",
    sort:str="asc"):
    names = []
    leads = []
    if show == "data":
        query = db.query(SheetData)
        if sort == "timestamp_desc":
            names = db.query(SheetData).order_by(SheetData.timestamp.desc()).all()
        elif sort == "timestamp_desc":
            names = db.query(SheetData).order_by(SheetData.timestamp.asc()).all()
        else:
            names = db.query(SheetData).order_by(SheetData.id).all()
        leads = db.query(SheetData.teamlead).distinct().all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "message": message,
        "names": names,
        "leads": leads,
        "sort":sort,
    })

@app.get('/dashboard/details/{id}',response_class=HTMLResponse)
def detail(id,request: Request, db: Session = Depends(get_db)):
    detail = db.query(SheetData).order_by(SheetData.id).filter(SheetData.id==id).first()
    return templates.TemplateResponse("details.html",{
        "request": request,
        "detail" : detail
    })

@app.get('/dashboard/agent_details/{email_address}',response_class=HTMLResponse)
def detail(email_address:str,request: Request, db: Session = Depends(get_db)):
    emails = db.query(SheetData).order_by(SheetData.id).filter(SheetData.email_address==email_address).all()
    return templates.TemplateResponse("details_by_email.html",{
        "request": request,
        "emails" : emails,
        "email_address": email_address
    })

@app.get('/dashboard/search-extension',response_class=HTMLResponse)
def redirect_to_search(extension_id:str):
    return RedirectResponse(
        url=f"/dashboard/search-extension/{extension_id}", 
        status_code=303
    )

@app.get('/dashboard/search-extension/{extension_id}',response_class=HTMLResponse)
def search(extension_id:str, request: Request, db: Session = Depends(get_db)):
    if extension_id:
        extension_by = db.query(SheetData).order_by(SheetData.timestamp).filter(SheetData.extension_id==extension_id).all()
        return templates.TemplateResponse("extension_by.html",{
        "request": request,
        "extension_id": extension_id,
        "extension_by": extension_by
    })


@app.get('/dashboard/search-lead', response_class=HTMLResponse)
def search_by_lead(teamlead: str, request: Request = None, db: Session = Depends(get_db)):
    selected_lead = []
    if teamlead:
        selected_lead = db.query(SheetData).order_by(SheetData.extension_id).filter(SheetData.teamlead == teamlead).all()
        return templates.TemplateResponse("selected_lead_details.html",{
            "request": request,
            "selected_lead": selected_lead,
            "teamlead": teamlead
        })
    return RedirectResponse(url="/dashboard", status_code=303)