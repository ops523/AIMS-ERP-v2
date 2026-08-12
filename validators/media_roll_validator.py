from services.service_result import ServiceResult


class MediaRollValidator:

    @staticmethod
    def validate_create(
        media_roll,
    ) -> ServiceResult:

        errors = []

        if not media_roll.product_id:

            errors.append(
                "Media Product is required."
            )

        if not media_roll.manufacturer_id:

            errors.append(
                "Manufacturer is required."
            )

        if not media_roll.supplier_id:

            errors.append(
                "Supplier is required."
            )

        if not media_roll.warehouse_id:

            errors.append(
                "Warehouse is required."
            )

        if media_roll.ordered_length_m <= 0:

            errors.append(
                "Ordered length must be greater than zero."
            )

        if media_roll.actual_length_m <= 0:

            errors.append(
                "Actual length must be greater than zero."
            )

        if media_roll.width_ft <= 0:

            errors.append(
                "Width must be greater than zero."
            )

        if media_roll.total_sqft <= 0:

            errors.append(
                "Total square feet must be greater than zero."
            )

        if media_roll.available_sqft < 0:

            errors.append(
                "Available square feet cannot be negative."
            )

        if (
            media_roll.available_sqft
            > media_roll.total_sqft
        ):

            errors.append(
                "Available square feet cannot exceed "
                "total square feet."
            )

        if errors:

            return ServiceResult.fail(
                "Media Roll validation failed.",
                errors,
            )

        return ServiceResult.ok()
