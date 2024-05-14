import json
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# Ścieżki do plików
ACCOUNT_BALANCE_FILE = 'data/account_balance.txt'
WAREHOUSE_PRODUCTS_FILE = 'data/warehouse_products.txt'
OPERATION_HISTORY_FILE = 'data/operation_history.txt'

# Funkcje do wczytywania i zapisywania danych
def load_data():
    try:
        with open(ACCOUNT_BALANCE_FILE, 'r') as f:
            account_balance = float(f.read())
    except FileNotFoundError:
        account_balance = 100000

    try:
        with open(WAREHOUSE_PRODUCTS_FILE, 'r') as f:
            warehouse_products = json.load(f)
    except FileNotFoundError:
        warehouse_products = [{"Produkt": "Płyta gipsowa", "Ilość": 1500, "Cena jednostkowa": 29.0}]

    try:
        with open(OPERATION_HISTORY_FILE, 'r') as f:
            operation_list = f.readlines()
    except FileNotFoundError:
        operation_list = []

    return account_balance, warehouse_products, operation_list

def save_data(account_balance, warehouse_products, operation_list):
    with open(ACCOUNT_BALANCE_FILE, 'w') as f:
        f.write(str(account_balance))
    with open(WAREHOUSE_PRODUCTS_FILE, 'w') as f:
        json.dump(warehouse_products, f)
    with open(OPERATION_HISTORY_FILE, 'w') as f:
        f.writelines(operation_list)

@app.route('/')
def index():
    account_balance, warehouse_products, _ = load_data()
    return render_template('index.html', account_balance=account_balance, warehouse_products=warehouse_products)

@app.route('/purchase', methods=['POST'])
def purchase():
    account_balance, warehouse_products, operation_list = load_data()
    product_name = request.form['product_name']
    unit_price = float(request.form['unit_price'])
    quantity = int(request.form['quantity'])
    total_cost = unit_price * quantity

    if account_balance >= total_cost:
        account_balance -= total_cost
        found = False
        for product in warehouse_products:
            if product['Produkt'] == product_name:
                product['Ilość'] += quantity
                product['Cena jednostkowa'] = unit_price
                found = True
                break
        if not found:
            warehouse_products.append({'Produkt': product_name, 'Ilość': quantity, 'Cena jednostkowa': unit_price})
        operation_list.append(f"Zakup: {product_name}, Cena jednostkowa: {unit_price}, Ilość: {quantity}\n")
        save_data(account_balance, warehouse_products, operation_list)
    return redirect(url_for('index'))

@app.route('/sale', methods=['POST'])
def sale():
    account_balance, warehouse_products, operation_list = load_data()
    product_name = request.form['product_name']
    unit_price = float(request.form['unit_price'])
    quantity = int(request.form['quantity'])

    for product in warehouse_products:
        if product['Produkt'] == product_name and product['Ilość'] >= quantity:
            product['Ilość'] -= quantity
            account_balance += unit_price * quantity
            operation_list.append(f"Sprzedaż: {product_name}, Cena jednostkowa: {unit_price}, Ilość: {quantity}\n")
            break
    save_data(account_balance, warehouse_products, operation_list)
    return redirect(url_for('index'))

@app.route('/balance', methods=['POST'])
def balance():
    account_balance, warehouse_products, operation_list = load_data()
    amount = float(request.form['amount'])
    comment = request.form['comment']
    account_balance += amount
    operation_list.append(f"Saldo zmienione o: {amount}, Komentarz: {comment}\n")
    save_data(account_balance, warehouse_products, operation_list)
    return redirect(url_for('index'))

@app.route('/historia/')
@app.route('/historia/<int:line_from>/<int:line_to>/')
def history(line_from=None, line_to=None):
    _, _, operation_list = load_data()
    if line_from is None or line_to is None:
        history_data = operation_list
    else:
        history_data = operation_list[line_from:line_to]
    return render_template('history.html', history_data=history_data)

if __name__ == '__main__':
    app.run(debug=True)
