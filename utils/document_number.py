from datetime import datetime


class DocumentNumber:

    @staticmethod
    def production_batch():

        return (
            "PB"
            + datetime.now().strftime("%y%m%d%H%M%S")
        )

    @staticmethod
    def printing_session():

        return (
            "PS"
            + datetime.now().strftime("%y%m%d%H%M%S")
        )

    @staticmethod
    def inventory_transaction():

        return (
            "IT"
            + datetime.now().strftime("%y%m%d%H%M%S")
        )

    @staticmethod
    def dispatch():

        return (
            "DP"
            + datetime.now().strftime("%y%m%d%H%M%S")
        )
