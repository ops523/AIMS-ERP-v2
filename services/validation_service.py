from __future__ import annotations


class ValidationService:

    @staticmethod
    def positive(value, field):

        if value <= 0:

            raise ValueError(

                f"{field} must be greater than zero."

            )

    @staticmethod
    def not_empty(value, field):

        if value is None:

            raise ValueError(

                f"{field} is mandatory."

            )

        if isinstance(value, str):

            if value.strip() == "":

                raise ValueError(

                    f"{field} is mandatory."

                )

    @staticmethod
    def roll_length(actual, ordered):

        if actual < ordered * 0.90:

            raise ValueError(

                "Roll appears too short."

            )

        if actual > ordered * 1.20:

            raise ValueError(

                "Roll length unusually high."

            )
