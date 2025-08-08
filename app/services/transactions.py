from dotenv import load_dotenv
from app.models.endpoint import *
from app.services.fatherService import FatherService

class TransactionService(FatherService):
    def __init__(self):
        super().__init__()

    def getAllTransactions(self):
        return

    def createTransaction(self):
        return