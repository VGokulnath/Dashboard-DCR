from fastapi import FastAPI, Request,Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from .import models
from app.db import SessionLocal, engine
from app.models import Base, SheetData
from app.utils.sheet import get_sheet_data
from sqlalchemy.orm import Session



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
def get_dashboard(request: Request, db: Session = Depends(get_db), message: str = "", show: str = ""):
    names = []
    if show == "data":
        names = db.query(SheetData).order_by(SheetData.id).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "message": message,
        "names": names
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
