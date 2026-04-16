from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/jigs", tags=["jigs"])

@router.get("/", response_model=list[schemas.JIGOut])
def list_jigs(db: Session = Depends(get_db)):
    return db.query(models.JIG).all()

@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total = db.query(models.JIG).count()
    in_use = db.query(models.JIG).filter(models.JIG.status == "in_use").count()
    return {"total": total, "in_use": in_use, "available": total - in_use}

@router.get("/{jig_id}", response_model=schemas.JIGOut)
def get_jig(jig_id: int, db: Session = Depends(get_db)):
    return db.query(models.JIG).filter(models.JIG.id == jig_id).first()

@router.delete("/{jig_id}")
def delete_jig(jig_id: int, db: Session = Depends(get_db)):
    jig = db.query(models.JIG).filter(models.JIG.id == jig_id).first()

    if not jig:
        raise HTTPException(status_code=404, detail="JIG not found")

    # xóa dữ liệu con trước (tránh lỗi foreign key)
    if hasattr(models, "SessionJig"):
        db.query(models.SessionJig)\
            .filter(models.SessionJig.jig_id == jig_id)\
            .delete(synchronize_session=False)

    db.delete(jig)
    db.commit()

    return {"ok": True, "deleted_id": jig_id}