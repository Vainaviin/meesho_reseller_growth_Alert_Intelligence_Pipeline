import sqlite3
import csv
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(
    BASE_DIR,
    "data",
    "meesho_reseller.db"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "part1_sql",
    "output"
)


os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_query(connection, query, output_file):

    cursor = connection.cursor()

    cursor.execute(query)

    rows = cursor.fetchall()

    columns = [
        description[0]
        for description in cursor.description
    ]

    output_path = os.path.join(
        OUTPUT_DIR,
        output_file
    )

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(columns)

        writer.writerows(rows)

    print(f"Created: {output_file}")


def main():

    connection = sqlite3.connect(DB_PATH)

    # 1. Monthly category revenue
    run_query(
        connection,
        """
        SELECT
            month,
            category,
            ROUND(SUM(quantity * unit_price), 2) AS revenue,
            COUNT(*) AS n_orders
        FROM orders
        GROUP BY month, category
        ORDER BY
            CASE month
                WHEN 'April' THEN 1
                WHEN 'May' THEN 2
                WHEN 'June' THEN 3
            END,
            category
        """,
        "monthly_category_revenue.csv"
    )


    # 2. Region revenue
    run_query(
        connection,
        """
        SELECT
            r.region,
            ROUND(
                SUM(o.quantity * o.unit_price),
                2
            ) AS revenue,
            COUNT(o.order_id) AS n_orders
        FROM orders o
        JOIN resellers r
            ON o.reseller_id = r.reseller_id
        GROUP BY r.region
        ORDER BY revenue DESC
        """,
        "region_revenue.csv"
    )


    # 3. Top resellers
    run_query(
        connection,
        """
        SELECT
            r.reseller_id,
            r.reseller_name,
            ROUND(
                SUM(o.quantity * o.unit_price),
                2
            ) AS total_spend
        FROM orders o
        JOIN resellers r
            ON o.reseller_id = r.reseller_id
        GROUP BY
            r.reseller_id,
            r.reseller_name
        HAVING total_spend > 50000
        ORDER BY total_spend DESC
        LIMIT 5
        """,
        "top_resellers.csv"
    )


    # 4A. Inactive resellers
    run_query(
        connection,
        """
        SELECT
            r.reseller_id,
            r.reseller_name,
            r.region
        FROM resellers r
        LEFT JOIN orders o
            ON r.reseller_id = o.reseller_id
        WHERE o.order_id IS NULL
        """,
        "inactive_resellers.csv"
    )


    # 4B. COUNT(*) vs COUNT(order_id)
    run_query(
        connection,
        """
        SELECT
            r.reseller_id,
            r.reseller_name,
            COUNT(*) AS total_rows,
            COUNT(o.order_id) AS matched_orders
        FROM resellers r
        LEFT JOIN orders o
            ON r.reseller_id = o.reseller_id
        WHERE r.reseller_id = 'RS024'
        GROUP BY
            r.reseller_id,
            r.reseller_name
        """,
        "left_join_count_demo.csv"
    )


    # 5. June Delivered AOV
    run_query(
        connection,
        """
        SELECT
            ROUND(
                SUM(quantity * unit_price) / COUNT(*),
                2
            ) AS june_delivered_aov
        FROM orders
        WHERE month = 'June'
          AND status = 'Delivered'
        """,
        "june_aov.csv"
    )


    connection.close()

    print("\nAll Part 1 queries completed successfully.")


if __name__ == "__main__":
    main()