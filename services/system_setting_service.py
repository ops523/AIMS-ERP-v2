from models.system_setting import SystemSetting


class SystemSettingService:

    @staticmethod
    def get(
        db,
        key,
        default=None,
    ):

        setting = (
            db.query(SystemSetting)
            .filter(
                SystemSetting.setting_key == key
            )
            .first()
        )

        if setting:

            return setting.setting_value

        return default

    @staticmethod
    def set(
        db,
        key,
        value,
        description="",
    ):

        setting = (
            db.query(SystemSetting)
            .filter(
                SystemSetting.setting_key == key
            )
            .first()
        )

        if setting:

            setting.setting_value = str(value)

        else:

            db.add(
                SystemSetting(
                    setting_key=key,
                    setting_value=str(value),
                    description=description,
                )
            )

        db.commit()
