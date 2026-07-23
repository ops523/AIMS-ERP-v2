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

        missing = [
            c
            for c in ExcelValidationService.REQUIRED_COLUMNS
            if c not in df.columns
        ]

        if missing:

            return False, [
                f"Missing Column : {c}"
                for c in missing
            ]

        if len(df) == 0:

            return False, [
                "Excel file contains no rows."
            ]

        df = df.fillna("")

        duplicates = df.duplicated().sum()

        if duplicates:

            errors.append(

                f"{duplicates} duplicate rows found."

            )

        for i, row in df.iterrows():

            if row["State"] == "":
                errors.append(

                    f"Row {i+2} : Missing State"

                )

            if row["District"] == "":
                errors.append(

                    f"Row {i+2} : Missing District"

                )

            if row["Town"] == "":
                errors.append(

                    f"Row {i+2} : Missing Town"

                )

        return len(errors) == 0, errors
