import os
import sqlite3
from datetime import datetime
import xlwings as xw
import logging

log_path = r"C:\Users\bholi\sigma_finance\sync_log.txt"

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("🚀 Sync script started.")


def normalize_key(name, amount, date_str):
    return (
        str(name).strip().lower(),
        round(float(amount), 2),
        date_str.strip()
    )


def fetch_new_payments(db_path):
    logging.info(f"📂 Using database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            user.name, 
            payment.amount, 
            payment.date
        FROM payment
        JOIN user ON payment.user_id = user.id
        ORDER BY payment.date ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    logging.info("🧾 Pulled %d rows from database.", len(rows))
    for row in rows[:5]:
        logging.info(f"👤 Found user: {row[0]}")
    return rows


def get_last_data_row(table, key_column_index=1):
    last_row = 0
    for i, row in enumerate(table.ListRows):
        cell_value = row.Range.Cells(1, key_column_index).Value
        if cell_value not in (None, "", 0):
            last_row = i + 1  # Excel is 1-based
    return last_row


def copy_formulas_from_previous_row(table, last_row_index, new_row):
    try:
        prev_row = table.ListRows(last_row_index - 1).Range
        new_row_range = new_row.Range

        formula_columns = [5, 9]  # Column E: Balance, Column I: Quarter

        for col_index in formula_columns:
            prev_cell = prev_row.Cells(1, col_index)
            new_cell = new_row_range.Cells(1, col_index)

            if prev_cell.HasFormula:
                new_cell.Formula = prev_cell.Formula
    except Exception as e:
        logging.warning(f"⚠️ Failed to copy formulas: {e}")


def sync_payments_to_excel(wb, sheet_name, table_name, db_rows, logger):
    sheet = wb.sheets[sheet_name]

    try:
        table = sheet.api.ListObjects(table_name)
    except Exception:
        logger.error(f"❌ Table '{table_name}' not found in sheet '{sheet_name}'.")
        return

    row_count = table.ListRows.Count
    logger.info(f"📊 Table '{table_name}' has {row_count} existing rows.")

    existing_keys = set()
    if table.DataBodyRange is not None:
        for row in table.DataBodyRange.Rows:
            name = row.Cells(1, 1).Value  # Column A
            date = row.Cells(1, 6).Value  # Column F
            if name and date:
                if isinstance(date, str):
                    try:
                        date = datetime.strptime(date, "%m/%d/%Y").date()
                    except ValueError:
                        continue
                elif isinstance(date, datetime):
                    date = date.date()
                existing_keys.add((name.strip().lower(), date, round(row.Cells(1, 4).Value, 2)))  # Column D
    else:
        logger.info("📭 Table is currently empty — no existing keys to compare.")

    rows_to_insert = []
    for row in db_rows:
        name = row["name"].strip()
        date_paid = row["date_paid"]
        amount_paid = row["amount_paid"]
        key = (name.strip().lower(), date_paid, round(amount_paid, 2))

        if key not in existing_keys:
            rows_to_insert.append(row)
        else:
            logger.info(f"⏭️ Skipped duplicate for {name} on {date_paid.strftime('%m/%d/%Y')} (${amount_paid})")

    for row in rows_to_insert:
        name = row["name"].strip()
        amount_paid = row["amount_paid"]
        date_paid = row["date_paid"]
        formatted_date = date_paid.strftime("%m/%d/%Y")

        last_data_row = get_last_data_row(table, key_column_index=1)
        new_row = table.ListRows.Add(Position=last_data_row + 1)

        copy_formulas_from_previous_row(table, last_data_row + 1, new_row)

        values = [
            name, "", "", amount_paid, "", formatted_date, "", "", ""
        ]

        for col_offset, value in enumerate(values):
            new_row.Range.Cells(1, col_offset + 1).Value = value

        logger.info(f"✅ Inserted payment for {name} on {formatted_date}")


def pull_dues_from_db(db_path=None):
    try:
        if db_path is None:
            db_path = r"C:\Users\bholi\sigma_finance\instance\site.db"

        wb_path = r"C:\Users\bholi\OneDrive\SDS Treasurer Documents\Financial Tracker_V2.xlsm"
        wb = xw.Book.caller() if xw.apps.count > 0 else xw.Book(wb_path)

        rows = fetch_new_payments(db_path)

        db_rows = []
        for name, amount_paid, raw_date in rows:
            try:
                date_paid = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S").date()
            except Exception as e:
                logging.warning(f"⚠️ Date parse failed for {raw_date}: {e}")
                continue

            db_rows.append({
                "name": name.strip(),
                "amount_paid": round(float(amount_paid), 2),
                "date_paid": date_paid
            })

        sync_payments_to_excel(wb, "Member Dues", "Dues", db_rows, logging)

    except Exception as e:
        logging.error(f"❌ Sync failed: {e}")