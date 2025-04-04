import re
import sys

import pandas as pd
from pypdf import PdfReader


def main(filename):
    reader = PdfReader(filename)
    total = float(
        reader.pages[0].extract_text().split("This month's charges $")[1].split("\n")[0]
    )

    bill_pages = ""
    for page in reader.pages[3:]:
        if "Talk activity" in (text := page.extract_text()):
            break
        bill_pages += text + "\n"

    records = []
    for ln, line in enumerate(lines := bill_pages.split("\n")):
        if re.match(r"\d{3}-\d{3}-\d{4}", line):
            number = line.strip()
            # deal with weird case that some device names won't show up
            pages_back = 2
            if number.startswith('347') and lines[ln - 1].startswith('Xuy'):
                pages_back = 1
            name, amount = (x.strip() for x in lines[ln - pages_back].split("$"))
            records.append((name, number, float(amount)))

    bill = pd.DataFrame(records, columns=["name", "number", "charge"])
    users = (
        bill.loc[~bill["number"].str.contains("Share"), ["name", "number"]]
        .set_index("number")["name"]
        .to_dict()
    )
    bill["name"] = bill["number"].str.split(" ").str[0].map(users)
    bill["charge"] = bill["charge"] - (10 / len(users)) * (
        ~bill["number"].str.contains("Share")
    )
    bill["total"] = bill.groupby("name")["charge"].transform("sum").round(2)

    assert round(bill["charge"].sum(), 2) == total
    bill.to_csv(f"{filename}.csv", index=None)


if __name__ == "__main__":
    main(sys.argv[1])
