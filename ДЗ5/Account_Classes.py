from datetime import datetime, timezone
import re
import pandas as pd

class Account:
    # Счётчик начинается с 1000
    _account_counter: int = 1000

    def __init__(self, account_holder: str, balance: float = 0) -> None:
        Account._account_counter += 1

        self.holder: str = account_holder
        self.account_number: str = (f'ACC-{Account._account_counter}')
        self._balance: float = balance
        # История транзакций представляет из себя список кортежей формата:
        # (номер счёта, тип операции, сумма операции, дата операции, сумма на счету, успех/неудача операции)
        self.operations_history: list[tuple[str, str, float, datetime, float, str]] = []

        self.balance_check()
        self.holder_name_check()
    
    def balance_check(self):
        if self._balance < 0:
            raise ValueError("balance cannot be negative")
    
    def holder_name_check(self):
        # Имя состоит из двух слов с заглавной буквы на кириллице либо латинице
        pattern = r'[А-ЯЁA-Z]{1}[а-яёa-z]+\s[А-ЯЁA-Z]{1}[а-яёa-z]+'
        match = re.fullmatch(pattern, self.holder)
        if not match:
            raise ValueError("Name is not correct")

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount
        # Что бы избежать возможных ошибок во времени, оно переводится в часовой пояс UTC+0
        self.operations_history.append((self.account_number, 'deposit', amount, datetime.now(timezone.utc), self._balance, 'success'))

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        
        if self._balance - amount >= 0:
            self._balance -= amount
            self.operations_history.append((self.account_number, 'withdraw', amount, datetime.now(timezone.utc), self._balance, 'success'))
        else:
            self.operations_history.append((self.account_number, 'withdraw', amount, datetime.now(timezone.utc), self._balance, 'fail'))

    def get_balance(self) -> float:
        return self._balance
     
    # возвращаем последние quantity операций, сумма которых больше filter_transactions
    def get_history(self, filter_transactions: float = 0, quantity: int = 5) -> str:
        
        quantity = -quantity

        filtered = [operation for operation in self.operations_history if operation[2] > filter_transactions]

        transactions: list = []
        for acc_number, kind, amount, date, balance, success in filtered[quantity:]:
            transactions.append(f'account number {acc_number}, kind: {kind}, amount: {amount}, date: {datetime.strftime(date, "%Y-%m-%d %H:%M:%S %Z")}, balance: {balance}, {success}')
        return "\n".join(transactions)


class SavingsAccount(Account):
    account_type: str = 'savings'

    def apply_interest(self, rate: float) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        rate_apply = (self._balance * (rate / 100))
        self._balance = round((self._balance + rate_apply), 2)
        self.operations_history.append((self.account_number, 'apply_interest', rate_apply, datetime.now(timezone.utc), self._balance, 'success'))

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        
        # Запрещено снимать больше половины существующего баланса за раз
        if self._balance - amount >= self._balance / 2:
            self._balance -= amount
            self.operations_history.append((self.account_number, 'withdraw', amount, datetime.now(timezone.utc), self._balance, 'success'))
        else:
            self.operations_history.append((self.account_number, 'withdraw', amount, datetime.now(timezone.utc), self._balance, 'fail'))


class CheckingAccount(Account):
    account_type: str = 'checking'
