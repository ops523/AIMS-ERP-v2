import pandas as pd


class ExcelValidationService:

    REQUIRED_COLUMNS = [
        "State",
        "District",
        "Town",
        "Wall Width (ft)",
        "Wall Height (ft)",
        "Qty",
    ]

    @staticmethod
    def validate(df: pd.DataFrame):

        errors = []

        for column in ExcelValidationService.REQUIRED_COLUMNS:

            if column not in df.columns:
                errors.append(
                    f"Missing column : {column}"
                )

        if errors:
            return False, errors

        if df.empty:
            errors.append("Excel file is empty.")

        return len(errors) == 0, errors
