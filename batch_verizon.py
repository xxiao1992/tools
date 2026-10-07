"""
Usage:
1. Put this script in the same folder as all Verizon bill PDFs,
   or pass the folder path when running it.
2. Make sure the folder contains only the Verizon PDFs you want to process.
3. Run:
       python process_verizon.py /path/to/verizon_folder
4. The script will:
   - scan all PDFs in the folder
   - calculate each person's total for each bill
   - combine all bills into one table
   - add a final Total column across all bills
   - save the result as verizon_combined.csv in the same folder

Recommended PDF naming:
    2026-01.pdf
    2026-02.pdf
    2026-03.pdf

Using YYYY-MM filenames keeps the output columns in chronological order.
"""

import re
import sys
from pathlib import Path

import pandas as pd
from pypdf import PdfReader


def parse_bill(filename):
    """
    Parse one Verizon PDF and return:
        name | total
    one row per user.
    """
    reader = PdfReader(filename)

    # Extract total bill amount
    page0_text = reader.pages[0].extract_text()

    m = re.search(
        r"This month's charges\s*\$\s*([0-9,]+\.[0-9]{2})",
        page0_text,
    )

    if not m:
        raise ValueError(
            f"Could not find total in {filename}. "
            f"Snippet: {page0_text[:200]!r}"
        )

    total = float(m.group(1).replace(",", ""))
    print(f"{Path(filename).name}: total found = ${total:.2f}")

    # Extract billing detail pages
    bill_pages = ""

    for page in reader.pages[3:]:
        text = page.extract_text()

        if "Talk activity" in text:
            break

        bill_pages += text + "\n"

    lines = bill_pages.split("\n")
    records = []

    for ln, line in enumerate(lines):
        if re.match(r"\d{3}-\d{3}-\d{4}", line):
            number = line.strip()

            # Deal with weird case where some device names don't show up
            pages_back = 2

            if (
                number.startswith("347")
                and ln >= 1
                and lines[ln - 1].startswith("Xuy")
            ):
                pages_back = 1

            name, amount = (
                x.strip()
                for x in lines[ln - pages_back].split("$")
            )

            records.append(
                (name, number, float(amount))
            )

    bill = pd.DataFrame(
        records,
        columns=["name", "number", "charge"],
    )

    # Build phone number -> user mapping
    users = (
        bill.loc[
            ~bill["number"].str.contains("Share"),
            ["name", "number"],
        ]
        .set_index("number")["name"]
        .to_dict()
    )

    bill["name"] = (
        bill["number"]
        .str.split(" ")
        .str[0]
        .map(users)
    )

    # Spread the $10 adjustment across users
    bill["charge"] = bill["charge"] - (
        10 / len(users)
    ) * (~bill["number"].str.contains("Share"))

    # Sanity check
    calculated_total = round(bill["charge"].sum(), 2)

    if calculated_total != round(total, 2):
        raise ValueError(
            f"{Path(filename).name}: "
            f"calculated ${calculated_total:.2f}, "
            f"but bill says ${total:.2f}"
        )

    # One row per person
    result = (
        bill.groupby("name", as_index=False)["charge"]
        .sum()
        .rename(columns={"charge": "total"})
    )

    result["total"] = result["total"].round(2)

    return result


def main(folder):
    folder = Path(folder)

    pdf_files = sorted(
        p for p in folder.glob("*.pdf")
        if p.is_file()
    )

    if not pdf_files:
        raise ValueError(f"No PDF files found in {folder}")

    print(f"Found {len(pdf_files)} PDFs\n")

    monthly_results = []

    for pdf_file in pdf_files:
        result = parse_bill(pdf_file)

        # Use filename without ".pdf" as the column name
        month_name = pdf_file.stem

        result = result.rename(
            columns={"total": month_name}
        )

        result = result.set_index("name")

        monthly_results.append(result)

    # Combine all months side-by-side
    combined = pd.concat(
        monthly_results,
        axis=1,
    ).fillna(0)

    # Add total across all bills
    combined["Total"] = combined.sum(axis=1).round(2)

    # Optional: add grand total row
    combined.loc["GRAND TOTAL"] = (
        combined.sum(axis=0).round(2)
    )

    combined = combined.reset_index()

    output_file = folder / "verizon_combined.csv"

    combined.to_csv(
        output_file,
        index=False,
    )

    print(f"\nSaved combined result to:")
    print(output_file)

    print("\nResult:")
    print(combined.to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1])