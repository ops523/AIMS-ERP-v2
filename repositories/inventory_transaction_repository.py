@staticmethod
def create(
    db,
    transaction,
):

    db.add(transaction)

    db.commit()

    db.refresh(transaction)

    return transaction
