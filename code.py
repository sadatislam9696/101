


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import qrcode
from fpdf import FPDF
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pymysql
import requests

# Global Variables for Google Sheets Setup
SERVICE_ACCOUNT_FILE = None  # Initially unset
SPREADSHEET_ID = None  # Initially unset
credentials = None
client = None
sheet = None
root = None
confidential_window = None
db_connection = None
db_cursor = None
PASSWORD = "1234"


# Function to authorize Google Sheets with the provided service account JSON file
def authorize_google_sheet():
    global credentials, client
    if not SERVICE_ACCOUNT_FILE:
        raise Exception("Service account file is not set. Please provide the JSON file first.")
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(credentials)


# Function to set the Sheet ID manually
def set_sheet_id():
    global SPREADSHEET_ID, sheet
    SPREADSHEET_ID = sheet_id_input.get()
    if not SPREADSHEET_ID:
        messagebox.showerror("Error", "Sheet ID is required.")
        return
    try:
        if not client:
            authorize_google_sheet()
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        messagebox.showinfo("Success", f"Successfully connected to the sheet: {SPREADSHEET_ID}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect to the sheet: {e}")


# Function to set the Service Account JSON file manually
def set_service_account_file():
    global SERVICE_ACCOUNT_FILE, credentials, client
    SERVICE_ACCOUNT_FILE = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not SERVICE_ACCOUNT_FILE:
        messagebox.showerror("Error", "Service account JSON file is required.")
        return
    try:
        authorize_google_sheet()
        messagebox.showinfo("Success", "Service account file updated and reauthorized successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to authorize with the selected file: {e}")


# Keep your original functionality unchanged
def customer_discount_analysis():
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            messagebox.showerror("Error", "No data available for analysis.")
            return

        total_expenses = df.groupby("Customer Name")["Expense"].sum()
        top_customers = total_expenses.nlargest(5)
        top_customers.plot(kind="bar", title="Top 5 Customers by Total Expense")
        plt.xlabel("Customer Name")
        plt.ylabel("Total Expense")
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to perform analysis: {e}")


# Keep other existing functionality intact...#sql using
  # Password to access the Confidential Options

# Function to connect to MySQL database
 # Password to access the Confidential Options
GOOGLE_SHEET_URL = "SPREADSHEET_ID"  # Replace with your Google Sheets URL

# Global variables for managing toggle system and MySQL connection
root = None
confidential_window = None
db_connection = None
db_cursor = None
sheet = None  # Google Sheets instance

# Function to connect to MySQL database
def connect_to_mysql():
    global db_connection, db_cursor
    try:
        db_connection = pymysql.connect(
            host="localhost",
            user="root",
            password="sadat",
            database="base"
        )
        db_cursor = db_connection.cursor()
        db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INT,
                customer_name VARCHAR(255),
                product_name VARCHAR(255),
                expense FLOAT,
                quantity_sold INT
            )
        """)
        db_connection.commit()
        messagebox.showinfo("Success", "Connected to MySQL database!")
    except pymysql.MySQLError as e:
        messagebox.showerror("Error", f"Failed to connect to MySQL: {e}")

# Function to connect to Google Sheets
def connect_to_google_sheets():
    global sheet
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('path_to_service_account.json', scope)  # Replace with your JSON key file path
        client = gspread.authorize(credentials)
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        messagebox.showinfo("Success", "Connected to Google Sheets!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect to Google Sheets: {e}")

# Function to save Google Sheets data to MySQL
import pymysql
from tkinter import messagebox

def save_to_mysql():
    try:
        if not sheet:
            messagebox.showerror("Error", "Google Sheets is not connected!")
            return

        # Fetch data from Google Sheets
        data = sheet.get_all_records()
        if not data:
            messagebox.showinfo("No Data", "No data available in the Google Sheet to save.")
            return

        # Save data to MySQL database
        for record in data:
            customer_id = record.get("Customer ID")
            customer_name = record.get("Customer Name")
            product_name = record.get("Product Name")
            expense = record.get("Expense")
            quantity_sold = record.get("Quantity Sold")

            # Check if the record already exists in the database
            db_cursor.execute("""
                SELECT quantity_sold FROM customers 
                WHERE customer_id = %s AND product_name = %s
            """, (customer_id, product_name))
            
            result = db_cursor.fetchone()

            if result:
                # If record exists, update the quantity_sold
                existing_quantity = result[0]
                new_quantity = existing_quantity + quantity_sold
                db_cursor.execute("""
                    UPDATE customers 
                    SET quantity_sold = %s 
                    WHERE customer_id = %s AND product_name = %s
                """, (new_quantity, customer_id, product_name))
            else:
                # If no matching record exists, insert a new row with ON DUPLICATE KEY UPDATE
                db_cursor.execute("""
                    INSERT INTO customers (customer_id, customer_name, product_name, expense, quantity_sold)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE quantity_sold = quantity_sold + VALUES(quantity_sold)
                """, (customer_id, customer_name, product_name, expense, quantity_sold))

        # Commit the transaction
        db_connection.commit()
        messagebox.showinfo("Success", "Data saved to MySQL database successfully!")
    except pymysql.MySQLError as e:
        messagebox.showerror("Error", f"Failed to save data to MySQL: {e}")

# Function to search customer data from MySQL
def search_from_mysql():
    customer_id = customer_id_sql_input.get()
    if not customer_id:
        messagebox.showerror("Error", "Customer ID is required to search.")
        return

    try:
        # Fetch all records with the given customer_id
        db_cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        records = db_cursor.fetchall()  # Fetch all matching records

        if records:
            # Prepare the message with all customer details
            customer_details = "\n".join([f"ID: {record[0]}\nName: {record[1]}\nProduct: {record[2]}\n"
                                         f"Expense: {record[3]}\nQuantity Sold: {record[4]}\n"
                                         f"{'-'*40}" for record in records])
            messagebox.showinfo("Customer Found", customer_details)
        else:
            messagebox.showinfo("Not Found", "No customer found with the given ID.")
    except pymysql.MySQLError as e:
        messagebox.showerror("Error", f"Failed to search customer: {e}")

def update_mysql():
    try:
        customer_id = customer_id_sql_input.get()
        new_expense = float(new_expense_input.get())
        if not customer_id or not new_expense:
            messagebox.showerror("Error", "Customer ID and new expense value are required.")
            return

        db_cursor.execute("UPDATE customers SET expense = %s WHERE customer_id = %s", (new_expense, customer_id))
        db_connection.commit()
        messagebox.showinfo("Success", "Customer expense updated successfully!")
    except pymysql.MySQLError as e:
        messagebox.showerror("Error", f"Failed to update customer: {e}")

# Function to delete customer data from MySQL
def delete_from_mysql():
    customer_id = customer_id_sql_input.get()
    if not customer_id:
        messagebox.showerror("Error", "Customer ID is required to delete.")
        return

    try:
        db_cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
        db_connection.commit()
        messagebox.showinfo("Success", "Customer data deleted successfully!")
    except pymysql.MySQLError as e:
        messagebox.showerror("Error", f"Failed to delete customer: {e}")

# Function to open the Confidential window
def open_confidential_window():
    global confidential_window
    if confidential_window is None or not tk.Toplevel.winfo_exists(confidential_window):
        confidential_window = tk.Toplevel(root)
        confidential_window.title("Confidential Options")
        confidential_window.geometry("500x400")

        # Save to MySQL button
        ttk.Button(confidential_window, text="Save Data to MySQL", command=save_to_mysql).pack(pady=10)

        # Search from MySQL
        search_frame = ttk.LabelFrame(confidential_window, text="Search from MySQL", padding=10)
        search_frame.pack(fill="x", padx=10, pady=5)

        global customer_id_sql_input
        customer_id_sql_input = tk.StringVar()
        ttk.Label(search_frame, text="Customer ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(search_frame, textvariable=customer_id_sql_input, width=30).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(search_frame, text="Search", command=search_from_mysql).grid(row=0, column=2, padx=5, pady=5)

        # Update MySQL
        update_frame = ttk.LabelFrame(confidential_window, text="Update MySQL", padding=10)
        update_frame.pack(fill="x", padx=10, pady=5)

        global new_expense_input
        new_expense_input = tk.StringVar()
        ttk.Label(update_frame, text="New Expense:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(update_frame, textvariable=new_expense_input, width=30).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(update_frame, text="Update", command=update_mysql).grid(row=1, column=2, padx=5, pady=5)

        # Delete from MySQL
        delete_frame = ttk.LabelFrame(confidential_window, text="Delete from MySQL", padding=10)
        delete_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(delete_frame, text="Delete", command=delete_from_mysql).pack(pady=10)

        # Back Button
        ttk.Button(confidential_window, text="Exit", command=lambda: confidential_window.destroy()).pack(pady=20)

# Function to prompt for password and proceed
def password_prompt():
    password_window = tk.Toplevel(root)
    password_window.title("Enter Password")
    password_window.geometry("300x150")

    ttk.Label(password_window, text="Enter Password:", font=("Arial", 12)).pack(pady=10)
    password_input = tk.StringVar()
    ttk.Entry(password_window, textvariable=password_input, show="*", width=20).pack(pady=5)

    def check_password():
        if password_input.get() == PASSWORD:
            password_window.destroy()
            open_confidential_window()
        else:
            messagebox.showerror("Access Denied", "Incorrect Password")

    ttk.Button(password_window, text="Submit", command=check_password).pack(pady=10)



# Connect to MySQL and Google Sh
# Add a new frame for Google Sheets connection



# Frame for Google Sheets connection
# Function to reset and allow connecting to a new sheet dynamically
def reset_google_connector():
    global SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, credentials, client, sheet
    SERVICE_ACCOUNT_FILE = None
    SPREADSHEET_ID = None
    credentials = None
    client = None
    sheet = None
    sheet_id_input.set("")  # Clear the Sheet ID input
    messagebox.showinfo("Reset", "Google Connector has been reset. Please provide new details.")


# Keep your original GUI functionality
# ...
# QR Code Generation Function
def generate_qr(data, file_name):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(file_name)
    return file_name


# PDF Generation Function
def generate_pdf(data, file_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Customer Report", ln=True, align="C")
    
    # Customer details
    for key, value in data["customer"].items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    pdf.ln(10)  # Add some space before listing expenses

    # Product expenses
    pdf.cell(200, 10, txt="Individual Product Expenses:", ln=True)
    for product in data["products"]:
        pdf.cell(200, 10, txt=f"Product: {product['name']} - Expense: {product['expense']}", ln=True)

    pdf.ln(10)  # Add space
    pdf.cell(200, 10, txt=f"Total Expense: {data['total_expense']}", ln=True)

    pdf.output(file_name)
    return file_name


# GUI Functions

def product_estimation_analysis():
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            messagebox.showerror("Error", "No data available for analysis.")
            return

        sales_trend = df.groupby("Product Name")["Quantity Sold"].sum()
        sales_trend.plot(kind="line", title="Sales Trend by Product")
        plt.xlabel("Product Name")
        plt.ylabel("Quantity Sold")
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to perform analysis: {e}")


def search_customer():
    customer_id = customer_id_input.get()
    if not customer_id:
        messagebox.showerror("Error", "Customer ID is required.")
        return

    try:
        data = sheet.get_all_records()
        customer_data = next(
            (customer for customer in data if str(customer["Customer ID"]) == str(customer_id)), None
        )

        if customer_data is None:
            messagebox.showinfo("Not Found", "Customer not found.")
            return

        # Gather individual expenses for the customer
        customer_expenses = [customer for customer in data if str(customer["Customer ID"]) == str(customer_id)]
        total_expense = sum(exp["Expense"] for exp in customer_expenses)
        
        # Prepare data for displaying and generating the PDF
        customer_info = {
            "Customer ID": customer_data["Customer ID"],
            "Customer Name": customer_data["Customer Name"],
            "Total Expense": total_expense
        }
        
        products = [{"name": exp["Product Name"], "expense": exp["Expense"]} for exp in customer_expenses]

        # Show the customer data in a new window
        show_customer_data_window(customer_info, products, total_expense)

        # Store the customer info and products for PDF generation
        global selected_customer_data
        selected_customer_data = {"customer": customer_info, "products": products, "total_expense": total_expense}

        

    except Exception as e:
        messagebox.showerror("Error", f"Failed to search customer: {e}")


def show_customer_data_window(customer_info, products, total_expense):
    # New window to display customer info and product expenses
    show_window = tk.Toplevel(root)
    show_window.title(f"Customer: {customer_info['Customer Name']}")

    customer_label = ttk.Label(show_window, text=f"Customer ID: {customer_info['Customer ID']}\n"
                                                f"Customer Name: {customer_info['Customer Name']}\n"
                                                f"Total Expense: {total_expense}")
    customer_label.pack(pady=10)

    ttk.Label(show_window, text="Individual Expenses:").pack()

    for product in products:
        ttk.Label(show_window, text=f"Product: {product['name']} - Expense: {product['expense']}").pack()

    ttk.Button(show_window, text="Report PDF", command=generate_customer_pdf).pack(pady=10)


def generate_customer_pdf():
    global selected_customer_data
    if selected_customer_data is None:
        messagebox.showerror("Error", "No customer selected for PDF generation.")
        return

    file_name = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if file_name:
        generate_pdf(selected_customer_data, file_name)
        messagebox.showinfo("Success", f"Customer report saved at {file_name}")


def show_customers():
    try:
        data = sheet.get_all_records()
        if not data:
            messagebox.showinfo("No Data", "No customers available.")
            return

        show_window = tk.Toplevel(root)
        show_window.title("All Customers")

        columns = list(data[0].keys())
        tree = ttk.Treeview(show_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for row in data:
            tree.insert("", tk.END, values=list(row.values()))

        tree.pack(fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch customers: {e}")




def generate_qr_and_pdf():
    # Get inputs
    product_name = product_name_input.get()
    price = product_price_input.get()
    expire_date = product_expiry_input.get()
    webapp_url = webapp_input.get()

    if product_name and price and expire_date and webapp_url:
        # Generate a dynamic URL for the web app
        qr_url = f"{webapp_url}?product_name={product_name}&expense={price}"

        # Generate QR Code
        file_name_qr = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if file_name_qr:
            qr = qrcode.make(qr_url)
            qr.save(file_name_qr)
            messagebox.showinfo("QR Code", f"QR Code saved at {file_name_qr}")

        # Generate PDF
        data_pdf = {"Product Name": product_name, "Price": price, "Expire Date": expire_date}
        file_name_pdf = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_name_pdf:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Product Information", ln=True, align="C")
            for key, value in data_pdf.items():
                pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align="L")
            pdf.output(file_name_pdf)
            messagebox.showinfo("PDF", f"PDF saved at {file_name_pdf}")

        # Notify user
        messagebox.showinfo("QR Code Generated", f"Scan the QR code to open the web app and enter ID/Name.")
    else:
        messagebox.showerror("Error", "All fields are required.")


# Main Application
root = tk.Tk()
root.title("Automated Bussiness Solution With Qr Code Intregation")

# Frame for Working Mode
working_frame = ttk.LabelFrame(root, text="Working Mode", padding=10)
working_frame.pack(fill="x", padx=10, pady=5)

# VIP Mode
vip_frame = ttk.LabelFrame(root, text="VIP Mode - Product QR & PDF", padding=10)
vip_frame.pack(fill="x", padx=10, pady=5)

product_name_input = tk.StringVar()
product_price_input = tk.StringVar()
product_expiry_input = tk.StringVar()
webapp_input=tk.StringVar()

ttk.Label(vip_frame, text="Product Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(vip_frame, textvariable=product_name_input, width=40).grid(row=0, column=1, padx=5, pady=5)

ttk.Label(vip_frame, text="Price:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(vip_frame, textvariable=product_price_input, width=40).grid(row=1, column=1, padx=5, pady=5)

ttk.Label(vip_frame, text="Expire Date:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(vip_frame, textvariable=product_expiry_input, width=40).grid(row=2, column=1, padx=5, pady=5)
ttk.Label(vip_frame, text="Web App Connect:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(vip_frame, textvariable=webapp_input, width=40).grid(row=3, column=1, padx=5, pady=5)

ttk.Button(vip_frame, text="Generate QR Code & PDF", command=generate_qr_and_pdf).grid(row=4, column=0, columnspan=2, padx=5, pady=10)
# Frame for Business Analysis
business_frame = ttk.LabelFrame(root, text="Business Analysis", padding=10)
business_frame.pack(fill="x", padx=10, pady=5)

ttk.Button(business_frame, text="Customer Discount Analysis", command=customer_discount_analysis).pack(side="left", padx=10)
ttk.Button(business_frame, text="Product Estimation Analysis", command=product_estimation_analysis).pack(side="left", padx=10)

# Search Customer
search_frame = ttk.LabelFrame(root, text="Search Customer", padding=10)
search_frame.pack(fill="x", padx=10, pady=5)

customer_id_input = tk.StringVar()
ttk.Label(search_frame, text="Customer ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(search_frame, textvariable=customer_id_input, width=40).grid(row=0, column=1, padx=5, pady=5)

# Separate buttons for Search and PDF Generation
ttk.Button(search_frame, text="Search Customer", command=search_customer).grid(row=1, column=0, padx=5, pady=10)


# Show Customers Button
ttk.Button(root, text="Show All Customers", command=show_customers).pack(padx=10, pady=10)
ttk.Button(root, text="Confidential", command=password_prompt).pack(padx=2,pady=2)
# Google Sheets Connector Frame
sheet_connector_frame = ttk.LabelFrame(root, text="Google Sheet Connector", padding=10)
sheet_connector_frame.pack(fill="x", padx=10, pady=5)

# Sheet ID input and buttons
sheet_id_input = tk.StringVar()
ttk.Label(sheet_connector_frame, text="Sheet ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(sheet_connector_frame, textvariable=sheet_id_input, width=40).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(sheet_connector_frame, text="Set Sheet ID", command=set_sheet_id).grid(row=0, column=2, padx=5, pady=5)

# Service Account File input and reset button
ttk.Button(sheet_connector_frame, text="Set Service Account File", command=set_service_account_file).grid(row=1, column=0, columnspan=2, pady=10)
ttk.Button(sheet_connector_frame, text="Reset Connector", command=reset_google_connector).grid(row=1, column=2, pady=10)

# Running the Tkinter loop

#second winow funtionality

# Main application function


    
connect_to_mysql()
connect_to_google_sheets()
    


# Run the main application



root.mainloop()

