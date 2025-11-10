"""
UMK Admin Routes
CRUD operations for UMK data management
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from services.umk_service import UMKService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/umk", tags=["UMK Admin"])

# Pydantic models
class UMKCreate(BaseModel):
    kabupaten_kota: str
    provinsi: str
    umk: int
    tahun: int
    region: Optional[str] = "unknown"
    is_active: Optional[bool] = True
    source: Optional[str] = "Manual Entry"
    notes: Optional[str] = ""
    created_by: Optional[str] = "admin"

class UMKUpdate(BaseModel):
    kabupaten_kota: Optional[str] = None
    provinsi: Optional[str] = None
    umk: Optional[int] = None
    tahun: Optional[int] = None
    region: Optional[str] = None
    is_active: Optional[bool] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class UMKResponse(BaseModel):
    id: int
    kabupaten_kota: str
    provinsi: str
    umk: int
    tahun: int
    region: Optional[str]
    is_active: bool
    source: Optional[str]
    notes: Optional[str]
    created_at: str
    updated_at: str
    created_by: Optional[str]

    @classmethod
    def from_orm_obj(cls, umk_obj):
        return cls(
            id=umk_obj.id,
            kabupaten_kota=umk_obj.kabupaten_kota,
            provinsi=umk_obj.provinsi,
            umk=umk_obj.umk,
            tahun=umk_obj.tahun,
            region=umk_obj.region,
            is_active=umk_obj.is_active,
            source=umk_obj.source,
            notes=umk_obj.notes,
            created_at=umk_obj.created_at.isoformat() if umk_obj.created_at else "",
            updated_at=umk_obj.updated_at.isoformat() if umk_obj.updated_at else "",
            created_by=umk_obj.created_by
        )

def get_umk_service(db: Session = Depends(get_db)) -> UMKService:
    return UMKService(db)

@router.get("/", response_model=dict)
async def get_umk_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    provinsi: Optional[str] = None,
    tahun: Optional[int] = None,
    is_active: Optional[bool] = None,
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Get UMK data list with filtering and pagination
    """
    try:
        result = umk_service.get_umk_list(
            skip=skip,
            limit=limit,
            search=search,
            provinsi=provinsi,
            tahun=tahun,
            is_active=is_active
        )

        # Convert to response format
        data = [UMKResponse.from_orm_obj(umk) for umk in result["data"]]

        return {
            "data": data,
            "total": result["total"],
            "skip": result["skip"],
            "limit": result["limit"]
        }

    except Exception as e:
        logger.error(f"Error getting UMK list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{umk_id}", response_model=UMKResponse)
async def get_umk_detail(
    umk_id: int,
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Get UMK data by ID
    """
    try:
        umk = umk_service.get_umk_by_id(umk_id)
        if not umk:
            raise HTTPException(status_code=404, detail="UMK data not found")

        return UMKResponse.from_orm_obj(umk)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting UMK detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=UMKResponse)
async def create_umk(
    umk_data: UMKCreate,
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Create new UMK data
    """
    try:
        umk = umk_service.create_umk(umk_data.dict())
        return UMKResponse.from_orm_obj(umk)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating UMK: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{umk_id}", response_model=UMKResponse)
async def update_umk(
    umk_id: int,
    umk_data: UMKUpdate,
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Update UMK data
    """
    try:
        # Filter out None values
        update_data = {k: v for k, v in umk_data.dict().items() if v is not None}

        umk = umk_service.update_umk(umk_id, update_data)
        if not umk:
            raise HTTPException(status_code=404, detail="UMK data not found")

        return UMKResponse.from_orm_obj(umk)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating UMK: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{umk_id}")
async def delete_umk(
    umk_id: int,
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Delete UMK data (soft delete)
    """
    try:
        success = umk_service.delete_umk(umk_id)
        if not success:
            raise HTTPException(status_code=404, detail="UMK data not found")

        return {"message": "UMK data deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting UMK: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-csv")
async def import_csv(
    file: UploadFile = File(...),
    created_by: str = Form("admin"),
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Import UMK data from CSV file
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")

        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')

        # Import data
        result = umk_service.bulk_import_from_csv(csv_content, created_by)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/overview")
async def get_umk_stats(
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Get UMK statistics overview
    """
    try:
        stats = umk_service.get_umk_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting UMK stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filters/provinces")
async def get_provinces_list(
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Get list of unique provinces for filter
    """
    try:
        provinces = umk_service.get_provinces_list()
        return {"provinces": provinces}

    except Exception as e:
        logger.error(f"Error getting provinces list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filters/years")
async def get_years_list(
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Get list of unique years for filter
    """
    try:
        years = umk_service.get_years_list()
        return {"years": years}

    except Exception as e:
        logger.error(f"Error getting years list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-update")
async def bulk_update_umk(
    umk_ids: List[int],
    update_data: UMKUpdate,
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Bulk update multiple UMK records
    """
    try:
        # Filter out None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

        updated_count = 0
        errors = []

        for umk_id in umk_ids:
            try:
                result = umk_service.update_umk(umk_id, update_dict)
                if result:
                    updated_count += 1
                else:
                    errors.append(f"UMK ID {umk_id} not found")
            except Exception as e:
                errors.append(f"UMK ID {umk_id}: {str(e)}")

        return {
            "updated_count": updated_count,
            "total_requested": len(umk_ids),
            "errors": errors
        }

    except Exception as e:
        logger.error(f"Error in bulk update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-delete")
async def bulk_delete_umk(
    umk_ids: List[int],
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Bulk delete multiple UMK records (soft delete)
    """
    try:
        deleted_count = 0
        errors = []

        for umk_id in umk_ids:
            try:
                success = umk_service.delete_umk(umk_id)
                if success:
                    deleted_count += 1
                else:
                    errors.append(f"UMK ID {umk_id} not found")
            except Exception as e:
                errors.append(f"UMK ID {umk_id}: {str(e)}")

        return {
            "deleted_count": deleted_count,
            "total_requested": len(umk_ids),
            "errors": errors
        }

    except Exception as e:
        logger.error(f"Error in bulk delete: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/csv")
async def export_umk_csv(
    search: Optional[str] = None,
    provinsi: Optional[str] = None,
    tahun: Optional[int] = None,
    is_active: Optional[bool] = None,
    umk_service: UMKService = Depends(get_umk_service)
):
    """
    Export UMK data to CSV
    """
    try:
        # Get filtered data
        result = umk_service.get_umk_list(
            skip=0,
            limit=10000,  # Large limit for export
            search=search,
            provinsi=provinsi,
            tahun=tahun,
            is_active=is_active
        )

        # Convert to CSV format
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'id', 'kabupaten_kota', 'provinsi', 'umk', 'tahun',
            'region', 'is_active', 'source', 'notes', 'created_at', 'updated_at', 'created_by'
        ])

        # Data rows
        for umk in result["data"]:
            writer.writerow([
                umk.id, umk.kabupaten_kota, umk.provinsi, umk.umk, umk.tahun,
                umk.region, umk.is_active, umk.source, umk.notes,
                umk.created_at, umk.updated_at, umk.created_by
            ])

        csv_content = output.getvalue()
        output.close()

        # Return as downloadable file
        from fastapi.responses import StreamingResponse
        import io

        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=umk_data_export.csv"}
        )

    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))