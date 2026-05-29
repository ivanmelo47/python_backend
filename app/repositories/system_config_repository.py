import json
from sqlalchemy.orm import Session
from app.models.system_config_model import SystemConfig

class SystemConfigRepository:
    def get_value(self, db: Session, key: str, default: any = None):
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if not config:
            return default
            
        if config.type == "boolean":
            return str(config.value).lower() in ("1", "true", "yes")
        elif config.type == "json":
            try:
                return json.loads(config.value)
            except Exception:
                return []
        
        return config.value

system_config_repository = SystemConfigRepository()
