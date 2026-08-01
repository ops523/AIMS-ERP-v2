from services.service_result import ServiceResult


class MediaRollValidator:

    @staticmethod
    def validate_create(media_roll):

        errors = []

        if not media_roll.media_product_id:
            errors.append("Media Product is required.")

        if not media_roll.manufacturer_id:
            errors.append("Manufacturer is required.")

        if not media_roll.supplier_id:
            errors.append("Supplier is required.")

        if not media_roll.warehouse_id:
            errors.append("Warehouse is required.")

        if media_roll.width_ft <= 0:
            errors.append("Width must be greater than zero.")

        if media_roll.actual_length_m <= 0:
            errors.append("Length must be greater than zero.")

        if errors:
            return ServiceResult.fail(
                "Validation failed.",
                errors
            )

        return ServiceResult.ok()
