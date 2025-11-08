from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from app.db.database import get_db
from typing import List, Dict, Any
import importlib
import pkgutil
from app import models

router = APIRouter()

@router.get("/models")
async def get_database_models(db: Session = Depends(get_db)):
    """Get all database models and their structure"""
    
    # Get all model classes
    model_info = []
    
    # Import all models from the models package
    for _, module_name, _ in pkgutil.iter_modules(models.__path__):
        try:
            module = importlib.import_module(f'app.models.{module_name}')
            # Get all classes from the module that are SQLAlchemy models
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    hasattr(attr, '__tablename__') and 
                    hasattr(attr, '__table__')):
                    
                    # Get table info
                    table = attr.__table__
                    inspector = inspect(db.bind)
                    
                    # Get column information
                    columns = []
                    for column in table.columns:
                        col_info = {
                            'name': column.name,
                            'type': str(column.type),
                            'nullable': column.nullable,
                            'primary_key': column.primary_key,
                            'foreign_keys': [str(fk.target_fullname) for fk in column.foreign_keys] if column.foreign_keys else [],
                            'default': str(column.default) if column.default else None
                        }
                        columns.append(col_info)
                    
                    # Get relationships
                    relationships = []
                    if hasattr(attr, '__mapper__'):
                        for rel in attr.__mapper__.relationships:
                            relationships.append({
                                'name': rel.key,
                                'target': rel.mapper.class_.__name__,
                                'type': 'one-to-many' if rel.uselist else 'many-to-one'
                            })
                    
                    # Try to get record count
                    try:
                        count_result = db.execute(text(f"SELECT COUNT(*) FROM {table.name}"))
                        record_count = count_result.scalar()
                    except Exception:
                        record_count = 0
                    
                    model_info.append({
                        'name': attr.__name__,
                        'table_name': table.name,
                        'description': attr.__doc__ or f'{attr.__name__} model',
                        'columns': columns,
                        'relationships': relationships,
                        'record_count': record_count,
                        'category': _get_model_category(attr.__name__)
                    })
                    
        except Exception as e:
            print(f"Error processing module {module_name}: {e}")
            continue
    
    return {
        'models': model_info,
        'total_models': len(model_info),
        'total_records': sum(model.get('record_count', 0) for model in model_info)
    }

@router.get("/models/{model_name}")
async def get_model_details(model_name: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific model"""
    
    # Find the model class
    for _, module_name, _ in pkgutil.iter_modules(models.__path__):
        try:
            module = importlib.import_module(f'app.models.{module_name}')
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    hasattr(attr, '__tablename__') and 
                    attr.__name__.lower() == model_name.lower()):
                    
                    table = attr.__table__
                    inspector = inspect(db.bind)
                    
                    # Get detailed column information
                    columns = []
                    for column in table.columns:
                        col_info = {
                            'name': column.name,
                            'type': str(column.type),
                            'nullable': column.nullable,
                            'primary_key': column.primary_key,
                            'foreign_keys': [str(fk.target_fullname) for fk in column.foreign_keys] if column.foreign_keys else [],
                            'default': str(column.default) if column.default else None,
                            'autoincrement': column.autoincrement,
                            'unique': column.unique if hasattr(column, 'unique') else False
                        }
                        columns.append(col_info)
                    
                    # Get indexes
                    indexes = []
                    try:
                        for index in inspector.get_indexes(table.name):
                            indexes.append({
                                'name': index['name'],
                                'columns': index['column_names'],
                                'unique': index['unique']
                            })
                    except Exception:
                        pass
                    
                    # Get foreign key constraints
                    foreign_keys = []
                    try:
                        for fk in inspector.get_foreign_keys(table.name):
                            foreign_keys.append({
                                'name': fk['name'],
                                'constrained_columns': fk['constrained_columns'],
                                'referred_table': fk['referred_table'],
                                'referred_columns': fk['referred_columns']
                            })
                    except Exception:
                        pass
                    
                    # Sample data
                    try:
                        sample_data = db.execute(text(f"SELECT * FROM {table.name} LIMIT 5")).fetchall()
                        sample_data = [dict(row._mapping) for row in sample_data]
                    except Exception:
                        sample_data = []
                    
                    return {
                        'name': attr.__name__,
                        'table_name': table.name,
                        'description': attr.__doc__ or f'{attr.__name__} model',
                        'columns': columns,
                        'indexes': indexes,
                        'foreign_keys': foreign_keys,
                        'sample_data': sample_data,
                        'category': _get_model_category(attr.__name__)
                    }
        except Exception as e:
            continue
    
    return {'error': 'Model not found'}

def _get_model_category(model_name: str) -> str:
    """Determine the category of a model based on its name"""
    name_lower = model_name.lower()
    
    if any(keyword in name_lower for keyword in ['user', 'role', 'branch', 'warehouse']):
        return 'core'
    elif any(keyword in name_lower for keyword in ['product', 'category', 'inventory', 'stock']):
        return 'inventory'
    elif any(keyword in name_lower for keyword in ['sales', 'customer', 'order']):
        return 'sales'
    elif any(keyword in name_lower for keyword in ['purchase', 'supplier', 'vendor']):
        return 'purchasing'
    elif any(keyword in name_lower for keyword in ['account', 'journal', 'ledger', 'currency']):
        return 'accounting'
    elif any(keyword in name_lower for keyword in ['pos', 'terminal', 'payment']):
        return 'pos'
    elif any(keyword in name_lower for keyword in ['cash', 'flow', 'transaction']):
        return 'cashflow'
    elif any(keyword in name_lower for keyword in ['expense']):
        return 'expenses'
    else:
        return 'other'
