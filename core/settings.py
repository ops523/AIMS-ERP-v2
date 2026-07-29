from sqlalchemy.orm import Session

from models.system_setting import SystemSetting


class Settings:

    _cache = {}


    @classmethod
    def get(cls, db: Session, key: str, default=None):

        if key in cls._cache:
            return cls._cache[key]

        setting = (
            db.query(SystemSetting)
            .filter(
                SystemSetting.setting_key == key
            )
            .first()
        )

        if setting:

            cls._cache[key] = setting.setting_value

            return setting.setting_value

        return default
