import argparse
import csv
from datetime import datetime

parser = argparse.ArgumentParser(description="Name of data file")
parser.add_argument("fileName")
args = parser.parse_args()

main = {}
invalid = {}
negative = {}
duplicates = {}
seen = {}
productBreakdown = {}
monthBreakdown = {}


def parse_date(date):
    if not date:
        return None
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        try:
            parsed_date = datetime.strptime(date, "%m/%d/%Y")
        except ValueError:
            return None
    return parsed_date


def parse_amount(amount):
    stripped = amount.strip()
    if not amount or not stripped:
        return None

    amountClean = stripped.replace("$", "").replace(",", "")
    try: 
        amountFormated = float(amountClean)
        return amountFormated
    except ValueError:
        return None

def parse_product(product):
    stripped = product.strip()
    if not product or not stripped:
        return None
    return stripped
 

with open (args.fileName, "r") as file:
    reader = csv.reader(file)
    header = next(reader)
    for i, row in enumerate(reader, start=1):
        if not row:
            invalid[i] = ["blank line"]
            continue
        record = dict(zip(header, row))
        reasons = []
        amountParsed = parse_amount(record["amount"])
        if amountParsed is None:
            reasons.append("bad amount")
        dateParsed = parse_date(record["date"])
        if dateParsed is None:
            reasons.append("bad date")
        productParsed = parse_product(record["product"])
        if productParsed is None:
            reasons.append("bad product")
        if reasons:
            invalid[i] = reasons
        else:
            main[i] = {"date": dateParsed, "product" : productParsed, "amount" : amountParsed}
            if amountParsed < 0:
                negative[i] = main[i]

            key = (dateParsed, productParsed, amountParsed)
            if key in seen:
                first_index = seen[key]
                if first_index not in duplicates:
                    duplicates[first_index] = []
                duplicates[first_index].append(i)
            else:
                seen[key] = i

            if productParsed not in productBreakdown:
                productBreakdown[productParsed] = {"count": 0, "revenue": 0}
            productBreakdown[productParsed]["count"] += 1
            productBreakdown[productParsed]["revenue"] += amountParsed


            monthKey = dateParsed.strftime("%Y-%m") 

            if monthKey not in monthBreakdown:
                monthBreakdown[monthKey] = {"count": 0, "revenue": 0}
            monthBreakdown[monthKey]["count"] += 1
            monthBreakdown[monthKey]["revenue"] += amountParsed





get_revenue = lambda pair: pair[1]["revenue"]
topProductRanked = sorted(productBreakdown.items(), key=get_revenue, reverse=True)          
print(topProductRanked)

print()


topMonthRanked = sorted(monthBreakdown.items(), reverse=False)
for key, value in topMonthRanked:
    print(key, value)


amounts = [row["amount"] for row in main.values()]

total = sum(amounts)
minimum = min(amounts)
maximum = max(amounts)
avg = total / len(amounts)

valid_count = len(main)
invalid_count = len(invalid)
rows_read = valid_count + invalid_count 

dates = [row["date"] for row in main.values()]
earliest = min(dates)
latest = max(dates)
                
