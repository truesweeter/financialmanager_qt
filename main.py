import sys
import sqlite3


from PyQt6.QtWidgets import QMainWindow, QApplication, QInputDialog, QDialog, QLineEdit, QMessageBox, QTableWidgetItem
from PyQt6 import uic
from PyQt6.QtCore import Qt

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

print("Program started.\n\n")
current_user = ""
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("qdialog.ui", self)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Вход")
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.setFixedSize(self.width(), self.height())

        self.current_user = ""

        self.registerButton.clicked.connect(self.register)
        self.loginButton.clicked.connect(self.login)
    
    def login(self):
        login = self.loginEdit.text()
        password = self.passwordEdit.text()
        success = True

        print(f"Login input - {login}, {password}\n")

        result = cursor.execute("""
                                SELECT * from users_data
                                WHERE login = ?
                                """, (login,)).fetchall()



        try:
            correct_login = result[0][1]
            correct_password = result[0][2]
            print(f"Correct data - {correct_login}, {correct_password}\n")
            if correct_password != password:
                success = False
            else:
                success = True
        except IndexError:
            success = False
            
    
        if not success:
            self.statusLabel.setText("Неверный логин или пароль")
            self.statusLabel.setStyleSheet("color: red;")
        
        if success:
            QMessageBox.information(self, "Успешно", "Вы успешно вошли в систему")
            self.current_user = cursor.execute("""SELECT * from users_data WHERE login = ?""", (login,)).fetchall()
            global current_user
            current_user = self.current_user
            print(f"Current user - {self.current_user}\n")
            self.mainwindow = Manager()
            self.mainwindow.show() 
            self.close()



    def register(self):
        login = self.loginEdit.text()
        password = self.passwordEdit.text()
        print(f"Register input - {login}, {password}\n")
        if login and password:
            result = cursor.execute("""
                                    SELECT * from users_data 
                                    WHERE login = ?
                                    """, (login,)).fetchall()
            print(f"Output - {result}")
            if not result:
                cursor.execute("""
                            INSERT INTO users_data (login, password) VALUES (?, ?)
                            """, (login, password))
                self.current_user = cursor.execute("""SELECT * from users_data WHERE login = ?""", (login,)).fetchall()
                global current_user
                current_user = self.current_user
                print(f"Current user - {self.current_user}\n")
                conn.commit()
                QMessageBox.information(self, "Успешно", "Вы успешно зарегистрировались")
                self.mainwindow = Manager()
                self.mainwindow.show() 
                self.close()
            else:
                self.statusLabel.setText("Пользователь с таким логином уже существует")
                self.statusLabel.setStyleSheet("color: red;")
        else:
            self.statusLabel.setText("Поля не могут быть пустыми")
            self.statusLabel.setStyleSheet("color: red;")



class Manager(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("design.ui", self)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Ваш Менеджер")
        self.setFixedSize(self.width(), self.height())
        global current_user
        self.current_user = current_user
        self.welcomeLabel.setText(f"Добро пожаловать, {self.current_user[0][1]}!")

        self.typesGroup.setExclusive(True)
        self.newTransaction.clicked.connect(self.create_transaction)

        self.amountEdit.hide()
        self.dateEdit.hide()
        self.descriptionEdit.hide()
        self.labelType.hide()
        self.incomeType.hide()
        self.expensesType.hide()
        self.cancelBtn.hide()
        self.categoryLabel.hide()
        for button in self.expensesCategories.buttons():
            button.hide()
        for button in self.incomeCategories.buttons():
            button.hide()
            
        self.incomeType.toggled.connect(self.on_type_toggled)
        self.expensesType.toggled.connect(self.on_type_toggled)

        self.update_table()
    
    def create_transaction(self):
        self.amountEdit.show()
        self.dateEdit.show()
        self.descriptionEdit.show()
        self.labelType.show()
        self.incomeType.show()
        self.expensesType.show()
        self.cancelBtn.show()
        self.statusLabel.setText("")


        self.newTransaction.setText("Подтвердить")
        try:
            self.newTransaction.clicked.disconnect()
        except TypeError:
            pass

        self.newTransaction.clicked.connect(self.confirm_transaction)
        try:
            self.cancelBtn.clicked.disconnect()
        except TypeError:
            pass
        self.cancelBtn.clicked.connect(self.cancel_transaction)
        
    def on_type_toggled(self, checked):
        if self.incomeType.isChecked():
            self.show_income_category()
        elif self.expensesType.isChecked():
            self.show_expenses_category()
        else:
            self.hide_all_categories()

    def show_expenses_category(self):
        self.categoryLabel.show()
        for btn in self.expensesCategories.buttons():
            btn.show()
        for btn in self.incomeCategories.buttons():
            btn.setChecked(False)
            btn.hide()

    def show_income_category(self):
        self.categoryLabel.show()
        for btn in self.incomeCategories.buttons():
            btn.show()
        for btn in self.expensesCategories.buttons():
            btn.setChecked(False)
            btn.hide()

    def hide_all_categories(self):
        self.categoryLabel.hide()
        for group in [self.expensesCategories, self.incomeCategories]:
            for btn in group.buttons():
                btn.setChecked(False)
                btn.hide()


    def confirm_transaction(self):
        amount = self.amountEdit.text()
        date = self.dateEdit.text()
        description = self.descriptionEdit.text()
        category = "Без категории"
        if self.incomeType.isChecked():
            transaction_type = "Доход"
            for btn in self.incomeCategories.buttons():
                if btn.isChecked():
                    category = btn.text()
        elif self.expensesType.isChecked():
            transaction_type = "Расход"
            for btn in self.expensesCategories.buttons():
                if btn.isChecked():
                    category = btn.text()


        success = True

        if not amount.isdigit():
            success = False
            self.statusLabel.setText("Сумма должна состоять только из цифр")  
            self.statusLabel.setStyleSheet("color: red;")
            print("Transaction error - incorrect amount")
        if amount:
            if amount[0] == 0:
                success = False
                self.statusLabel.setText("Сумма не может начинаться с '0'")
                self.statusLabel.setStyleSheet("color: red;")
                print("Transaction error - incorrect amount")
        if amount == "":
            success = False
            self.statusLabel.setText("Пожалуйста, укажите сумму")
            self.statusLabel.setStyleSheet("color: red;")
            print("Transaction error - incorrect amount")   

        try:
            correct = False
            if date[2] == "." and date[5] == ".":
                if date[0].isdigit() and date[1].isdigit() and date[3].isdigit() and date[4].isdigit() and date[6].isdigit() and date[7].isdigit() and date[8].isdigit() and date[9].isdigit():
                    correct = True
                    try:
                        if int(date[3] + date[4]) > 12 or len(date[6:]) > 4:
                            success = False
                            self.statusLabel.setText("Пожалуйста, выберите существующую дату")
                            self.statusLabel.setStyleSheet("color: red;")
                            print("Transaction error - incorrect date")
                    except ValueError:
                        success = False

        except IndexError:
            correct = False
        if not correct:
            success = False
            self.statusLabel.setText("Заполните дату по верной форме")
            self.statusLabel.setStyleSheet("color: red;")
            print("Transaction error - incorrect date")


        if not (self.incomeType.isChecked() or self.expensesType.isChecked()):
            success = False
            self.statusLabel.setText("Необходимо выбрать тип транзакции")
            self.statusLabel.setStyleSheet("color: red;")
            print("Transaction error - incorrect type")


        if success:
            cursor.execute("""
                            INSERT into transactions (user_id, amount, type, description, date, category)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """, (current_user[0][0], amount, transaction_type, description, date, category))
            conn.commit()
            self.statusLabel.setText("Транзакция успешно добавлена!")
            self.statusLabel.setStyleSheet("color: green;")
            print("Transaction added")
            self.cancel_transaction()
            self.hide_all_categories()
            self.categoryLabel.hide()
            self.incomeType.setChecked(False)
            self.expensesType.setChecked(False)
        print("\n")
        self.update_table()

    def cancel_transaction(self):
        self.amountEdit.setText("")
        self.dateEdit.setText("")
        self.descriptionEdit.setText("")
        self.newTransaction.setText("Создать транзакцию")
        self.incomeType.setChecked(False)
        self.expensesType.setChecked(False)
        self.amountEdit.hide()
        self.dateEdit.hide()
        self.descriptionEdit.hide()
        self.labelType.hide()
        self.incomeType.hide()
        self.expensesType.hide()
        self.cancelBtn.hide()

        try:
            self.newTransaction.clicked.disconnect()
        except TypeError:
            pass

        self.newTransaction.clicked.connect(self.create_transaction)


    def update_table(self):
        cursor = conn.cursor()
        user = current_user[0][0]
        rows = cursor.execute("""
                                SELECT amount, type, description, date, category from transactions
                                WHERE user_id = ?
                                    """, (user,)).fetchall()
        print(f"Table updated - {rows}\n")

        self.transactionsTable.setRowCount(0)
        self.transactionsTable.setColumnCount(5)
        self.transactionsTable.setHorizontalHeaderLabels(["Сумма", "Тип", "Описание", "Дата", "Категория"])

        for row_data in rows:
            row_position = self.transactionsTable.rowCount()
            self.transactionsTable.insertRow(row_position)
            for col, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.transactionsTable.setItem(row_position, col, item)

        self.transactionsTable.resizeColumnsToContents()

            


if __name__ == "__main__":
    app = QApplication(sys.argv)

    loginDialog = LoginDialog()
    loginDialog.show()

    sys.exit(app.exec())