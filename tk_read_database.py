import pymysql
from pymysql import MySQLError
import datetime
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, messagebox, Frame, END, RIGHT, Y

# 函數：查詢資料庫中的品牌信息
def fetch_brands(name, cursor, result_text):
    try:
        query = f"SELECT * FROM `{name}`"
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result_text.delete(1.0, END)
        result_text.insert(END,f'資料庫 {name}:\n')
        result_text.insert(END, f"{' | '.join(columns)}\n")
        result_text.insert(END, '-' * 50 + '\n')
        for row in results:
            result_text.insert(END, f"{' | '.join(map(str, row))}\n")
    except MySQLError as e:
        messagebox.showerror("Error", f"Error: {e}")

# 函數：查詢過去一年銷量最高的兩個品牌
def fetch_top_brands(cursor, result_text):
    try:
        query = """
            SELECT Brand_ID, COUNT(*) AS units_sold
            FROM vehicle
            WHERE Sale_Date IS NOT NULL
              AND Sale_Date >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 YEAR), '%Y.%m')
            GROUP BY Brand_ID
            ORDER BY units_sold DESC
            LIMIT 2
        """
        cursor.execute(query)
        results = cursor.fetchall()
        result_text.delete(1.0, END)
        result_text.insert(END,"去一年銷量最高的兩個品牌:\n")
        result_text.insert(END, "Brand_ID \n")
        result_text.insert(END, '-' * 15+ '\n')
        for row in results:
            result_text.insert(END, f"{row[0]} \n")
    except MySQLError as e:
        messagebox.showerror("Error", f"Error: {e}")

# 函數：查詢最近一年銷售額最高的經銷商
def fetch_top_dealer(cursor, result_text, start_date, end_date):
    try:
        query = f"""
            SELECT d.Name, SUM(v.Value_car) AS Total_Sales
            FROM vehicle v
            JOIN Dealer d ON v.Dealer_ID = d.Dealer_ID
            WHERE v.Sale_Date IS NOT NULL
            AND v.Sale_Date BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY v.Dealer_ID
            ORDER BY Total_Sales DESC
            LIMIT 1;
        """
        cursor.execute(query)
        result = cursor.fetchone()
        result_text.delete(1.0, END)
        if result:
            result_text.insert(END,"最近一年銷售額最高的經銷商:\n")
            result_text.insert(END, "Dealer_ID | Total Sales\n")
            result_text.insert(END, '-' * 30 + '\n')
            result_text.insert(END, f"{result[0]} | {result[1]}\n")
        else:
            result_text.insert(END, "No results found.")
    except MySQLError as e:
        messagebox.showerror("Error", f"Error: {e}")

# 函數：查詢查看SUV銷量最好的月份
def fetch_best_suv_month(cursor, result_text,start_date, end_date):
    try:
        query = f"""
            SELECT DATE_FORMAT(Sale_Date, '%Y-%m') AS Sale_Month, COUNT(*) AS SUV_Sales
            FROM vehicle
            JOIN Model ON vehicle.Model_ID = Model.Model_ID
            WHERE Sale_Date IS NOT NULL
            AND Model.Body_style = 'SUV'
            AND Sale_Date BETWEEN '{start_date}'AND '{end_date}'
            
            ORDER BY SUV_Sales DESC
            LIMIT 1;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        result_text.delete(1.0, END)
        if results:
            result_text.insert(END, "SUV銷量最好的月份\n")
            result_text.insert(END, '-' * 10+ '\n')
            for row in results:
                result_text.insert(END, f"{row[1]}月\n")
        else:
            result_text.insert(END, "No results found.")
    except MySQLError as e:
        messagebox.showerror("Error", f"Error: {e}")

# 函數：查詢最長平均保留車輛庫存時間的經銷商
def fetch_longest_inventory_time_dealer(cursor, result_text):
    try:
        query = """
            SELECT d.Name, AVG(DATEDIFF(Sale_Date, Entry_Date)) AS Avg_Inventory_Time
            FROM vehicle v
            JOIN Dealer d ON v.Dealer_ID = d.Dealer_ID
            WHERE v.Sale_Date IS NOT NULL
            GROUP BY v.Dealer_ID
            ORDER BY Avg_Inventory_Time DESC
            LIMIT 1;
        """
        cursor.execute(query)
        result = cursor.fetchone()
        result_text.delete(1.0, END)
        if result:
            result_text.insert(END,"長平均保留車輛庫存時間的經銷商:\n")
            result_text.insert(END, "Dealer Name  \n")
            result_text.insert(END, '-' * 15 + '\n')
            result_text.insert(END, f"{result[0]} \n")
        else:
            result_text.insert(END, "No results found.")
    except MySQLError as e:
        messagebox.showerror("Error", f"Error: {e}")

# 函數：查詢供應商Getrag在兩個給定日期之間製造的有缺陷的變速器
def fetch_defective_transmissions(cursor, result_text, start_date, end_date):
    try:
        query = """
            SELECT dt.vin, c.Customer_Name
            FROM
            (
                SELECT vin
                FROM vehicle
                WHERE Transmissiondate BETWEEN %s AND %s
                AND Supplier_ID IN (
                    SELECT Supplier_ID
                    FROM Plant
                    WHERE Plant_Name = 'EliteGlobe' OR Plant_Name = 'HorizonTech'
                )
            ) AS dt
            JOIN
            (
                SELECT vin, Customer_ID
                FROM vehicle
                WHERE Status_ID = 'Sold'
            ) AS sc ON dt.vin = sc.vin
            JOIN customer c ON sc.Customer_ID = c.Customer_ID;
        """
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()
        result_text.delete(1.0, END)
        result_text.insert(END,"Getrag製造的有缺陷的變速器的車輛與客戶：\n")
        result_text.insert(END, "VIN | Customer Name\n")
        result_text.insert(END, '-' * 50 + '\n')
        for row in results:
            result_text.insert(END, f"{row[0]} | {row[1]}\n")
    except MySQLError as e:
        messagebox.showerror("Error", f"Error: {e}")

def exit():
    sys.exit()

# 建立GUI應用程式
def create_gui():
    root = Tk()
    root.title("資料庫報告")
    root.geometry("900x700")
    root.configure(bg='#f0f0f0')

    Label(root, text="Current time:", font=("Helvetica", 14), bg='#f0f0f0').pack(pady=5)
    now = datetime.datetime.now()
    now_time = now.strftime('%Y-%m-%d %H:%M:%S')
    Label(root, text=now_time, font=("Helvetica", 14), bg='#f0f0f0').pack(pady=5)

    Label(root, text="輸入想查詢的資料表名：", font=("Helvetica", 14), bg='#f0f0f0').pack(pady=10)

    table_name_entry = Entry(root, font=("Helvetica", 12), width=40)
    table_name_entry.pack(pady=5)

    result_frame = Frame(root, bg='#f0f0f0')
    result_frame.pack(pady=10)
    scrollbar = Scrollbar(result_frame)
    scrollbar.pack(side=RIGHT, fill=Y)
    result_text = Text(result_frame, height=20, width=100, font=("Helvetica", 12), yscrollcommand=scrollbar.set)
    result_text.pack()
    scrollbar.config(command=result_text.yview)

    connection = pymysql.connect(
        host='0.tcp.jp.ngrok.io',
        port=11051,
        user='411177035',
        password='411177035',
        database='411177035'
    )

    cursor = connection.cursor()

    def on_fetch_brands():
        fetch_brands(table_name_entry.get(), cursor, result_text)

    def on_fetch_top_brands():
        fetch_top_brands(cursor, result_text)

    def on_fetch_top_dealer():
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        fetch_top_dealer(cursor, result_text, start_date, end_date)

    def on_fetch_best_suv_month():
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        fetch_best_suv_month(cursor, result_text,start_date, end_date)

    def on_fetch_longest_inventory_time_dealer():
        fetch_longest_inventory_time_dealer(cursor, result_text)

    def on_fetch_defective_transmissions():
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        fetch_defective_transmissions(cursor, result_text, start_date, end_date)

    Button(root, text="查詢資料表", command=on_fetch_brands, font=("Helvetica", 12)).pack(pady=5)

    Button(root, text="過去一年銷量最高的兩個品牌", command=on_fetch_top_brands, font=("Helvetica", 12)).pack(pady=5)

    Label(root, text="請輸入起始日期（YYYY-MM）：", font=("Helvetica", 12), bg='#f0f0f0').pack(pady=5)
    start_date_entry = Entry(root, font=("Helvetica", 12), width=20)
    start_date_entry.pack(pady=5)

    Label(root, text="請輸入結束日期（YYYY-MM）：", font=("Helvetica", 12), bg='#f0f0f0').pack(pady=5)
    end_date_entry = Entry(root, font=("Helvetica", 12), width=20)
    end_date_entry.pack(pady=5)

    Button(root, text="最近一年銷售額最高的經銷商", command=on_fetch_top_dealer, font=("Helvetica", 12)).pack(pady=5)

    Button(root, text="SUV銷量最好的月份", command=on_fetch_best_suv_month, font=("Helvetica", 12)).pack(pady=5)

    Button(root, text="平均保留車輛庫存時間最長的經銷商", command=on_fetch_longest_inventory_time_dealer, font=("Helvetica", 12)).pack(pady=5)

    Button(root, text="供應商Getrag製造的有缺陷的變速器的車輛與客戶", command=on_fetch_defective_transmissions, font=("Helvetica", 12)).pack(pady=5)

    Button(root, text='離開', command=exit, font=("Helvetica", 12)).pack(pady=10)

    root.mainloop()

    cursor.close()
    connection.close()

if __name__ == "__main__":
    create_gui()
