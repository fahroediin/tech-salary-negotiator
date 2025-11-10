"""
UMK Management Service
Handles CRUD operations for UMK data
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database import UMKData
import pandas as pd
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UMKService:
    def __init__(self, db: Session):
        self.db = db

    def get_umk_list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        provinsi: Optional[str] = None,
        tahun: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get UMK data list with filtering and pagination
        """
        query = self.db.query(UMKData)

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    UMKData.kabupaten_kota.ilike(search_term),
                    UMKData.provinsi.ilike(search_term),
                    UMKData.region.ilike(search_term)
                )
            )

        if provinsi:
            query = query.filter(UMKData.provinsi.ilike(f"%{provinsi}%"))

        if tahun:
            query = query.filter(UMKData.tahun == tahun)

        if is_active is not None:
            query = query.filter(UMKData.is_active == is_active)

        # Get total count
        total = query.count()

        # Apply pagination
        umk_data = query.order_by(UMKData.provinsi, UMKData.kabupaten_kota).offset(skip).limit(limit).all()

        return {
            "data": umk_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    def get_umk_by_id(self, umk_id: int) -> Optional[UMKData]:
        """
        Get UMK data by ID
        """
        return self.db.query(UMKData).filter(UMKData.id == umk_id).first()

    def create_umk(self, umk_data: Dict[str, Any]) -> UMKData:
        """
        Create new UMK data
        """
        # Check for existing record
        existing = self.db.query(UMKData).filter(
            and_(
                UMKData.kabupaten_kota == umk_data["kabupaten_kota"],
                UMKData.provinsi == umk_data["provinsi"],
                UMKData.tahun == umk_data["tahun"]
            )
        ).first()

        if existing:
            raise ValueError(f"UMK data for {umk_data['kabupaten_kota']}, {umk_data['provinsi']} tahun {umk_data['tahun']} already exists")

        umk_record = UMKData(**umk_data)
        self.db.add(umk_record)
        self.db.commit()
        self.db.refresh(umk_record)

        logger.info(f"Created UMK record: {umk_record.kabupaten_kota}, {umk_record.provinsi} ({umk_record.tahun})")
        return umk_record

    def update_umk(self, umk_id: int, umk_data: Dict[str, Any]) -> Optional[UMKData]:
        """
        Update UMK data
        """
        umk_record = self.db.query(UMKData).filter(UMKData.id == umk_id).first()
        if not umk_record:
            return None

        # Check for duplicate (excluding current record)
        if "kabupaten_kota" in umk_data or "provinsi" in umk_data or "tahun" in umk_data:
            kabupaten_kota = umk_data.get("kabupaten_kota", umk_record.kabupaten_kota)
            provinsi = umk_data.get("provinsi", umk_record.provinsi)
            tahun = umk_data.get("tahun", umk_record.tahun)

            existing = self.db.query(UMKData).filter(
                and_(
                    UMKData.kabupaten_kota == kabupaten_kota,
                    UMKData.provinsi == provinsi,
                    UMKData.tahun == tahun,
                    UMKData.id != umk_id
                )
            ).first()

            if existing:
                raise ValueError(f"UMK data for {kabupaten_kota}, {provinsi} tahun {tahun} already exists")

        # Update fields
        for field, value in umk_data.items():
            if hasattr(umk_record, field):
                setattr(umk_record, field, value)

        umk_record.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(umk_record)

        logger.info(f"Updated UMK record: {umk_record.kabupaten_kota}, {umk_record.provinsi} ({umk_record.tahun})")
        return umk_record

    def delete_umk(self, umk_id: int) -> bool:
        """
        Delete UMK data (soft delete by setting is_active=False)
        """
        umk_record = self.db.query(UMKData).filter(UMKData.id == umk_id).first()
        if not umk_record:
            return False

        umk_record.is_active = False
        umk_record.updated_at = datetime.utcnow()
        self.db.commit()

        logger.info(f"Deactivated UMK record: {umk_record.kabupaten_kota}, {umk_record.provinsi} ({umk_record.tahun})")
        return True

    def bulk_import_from_csv(self, csv_content: str, created_by: str) -> Dict[str, Any]:
        """
        Bulk import UMK data from CSV content
        """
        try:
            # Parse CSV
            df = pd.read_csv(io.StringIO(csv_content))

            # Validate required columns
            required_columns = ['kabupaten_kota', 'provinsi', 'umk', 'tahun']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

            # Process each row
            success_count = 0
            error_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    umk_data = {
                        'kabupaten_kota': str(row['kabupaten_kota']).strip(),
                        'provinsi': str(row['provinsi']).strip(),
                        'umk': int(row['umk']),
                        'tahun': int(row['tahun']),
                        'region': str(row.get('region', '')).strip() or 'unknown',
                        'is_active': bool(row.get('is_active', True)),
                        'source': str(row.get('source', 'CSV Import')).strip(),
                        'notes': str(row.get('notes', '')).strip(),
                        'created_by': created_by
                    }

                    # Check for existing record
                    existing = self.db.query(UMKData).filter(
                        and_(
                            UMKData.kabupaten_kota == umk_data["kabupaten_kota"],
                            UMKData.provinsi == umk_data["provinsi"],
                            UMKData.tahun == umk_data["tahun"]
                        )
                    ).first()

                    if existing:
                        # Update existing record
                        for field, value in umk_data.items():
                            if hasattr(existing, field):
                                setattr(existing, field, value)
                        existing.updated_at = datetime.utcnow()
                        success_count += 1
                    else:
                        # Create new record
                        umk_record = UMKData(**umk_data)
                        self.db.add(umk_record)
                        success_count += 1

                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index + 2}: {str(e)}")

            self.db.commit()

            result = {
                'success': True,
                'processed': len(df),
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:10]  # Limit errors to first 10
            }

            logger.info(f"Bulk import completed: {success_count} successful, {error_count} errors")
            return result

        except Exception as e:
            self.db.rollback()
            logger.error(f"Bulk import failed: {str(e)}")
            raise ValueError(f"Bulk import failed: {str(e)}")

    def get_provinces_list(self) -> List[str]:
        """
        Get list of unique provinces
        """
        provinces = self.db.query(UMKData.provinsi).distinct().all()
        return [province[0] for province in provinces if province[0]]

    def get_years_list(self) -> List[int]:
        """
        Get list of unique years
        """
        years = self.db.query(UMKData.tahun).distinct().all()
        return sorted([year[0] for year in years if year[0]])

    def get_umk_stats(self) -> Dict[str, Any]:
        """
        Get UMK statistics
        """
        total_records = self.db.query(UMKData).count()
        active_records = self.db.query(UMKData).filter(UMKData.is_active == True).count()

        # Stats by year
        year_stats = self.db.query(
            UMKData.tahun,
            func.count(UMKData.id).label('count')
        ).group_by(UMKData.tahun).all()

        # Stats by province
        province_stats = self.db.query(
            UMKData.provinsi,
            func.count(UMKData.id).label('count')
        ).group_by(UMKData.provinsi).order_by(func.count(UMKData.id).desc()).limit(10).all()

        return {
            'total_records': total_records,
            'active_records': active_records,
            'inactive_records': total_records - active_records,
            'years': [{'year': stat[0], 'count': stat[1]} for stat in year_stats],
            'top_provinces': [{'province': stat[0], 'count': stat[1]} for stat in province_stats]
        }