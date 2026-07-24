from sqlalchemy import func


class CodeGenerator:

    @staticmethod
    def generate(
        db,
        model,
        code_field: str,
        prefix: str,
        digits: int = 6,
    ):

        column = getattr(model, code_field)

        latest = (
            db.query(column)
            .filter(column.like(f"{prefix}-%"))
            .order_by(column.desc())
            .first()
        )

        if latest is None:
            number = 1

        else:

            last_code = latest[0]

            try:
                number = int(last_code.split("-")[-1]) + 1

            except Exception:
                number = 1

        return f"{prefix}-{number:0{digits}d}"
