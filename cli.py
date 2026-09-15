import argparse
import csv
from datetime import datetime

parser = argparse.ArgumentParser(description="Name of data file")
parser.add_argument("fileName")
parser.add_argument("-n", "--top", type=int, default=5)
args = parser.parse_args()

main = {}
invalid = {}
negative = {}
duplicates = {}
seen = {}
productBreakdown = {}
monthBreakdown = {}
reasonsBreakdown = {}


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
            invalid[i] = {"rowData": row, "reasons": ["blank line"]}
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
            invalid[i] = {"rowData": record, "reasons": reasons}

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



for values in invalid.values():
    for reason in values["reasons"]:
        if reason not in reasonsBreakdown:
            reasonsBreakdown[reason] = {"count": 0}
        reasonsBreakdown[reason]["count"] += 1


get_revenue = lambda pair: pair[1]["revenue"]
topProductRanked = sorted(productBreakdown.items(), key=get_revenue, reverse=True)          
print(topProductRanked)

print()


topMonthRanked = sorted(monthBreakdown.items(), reverse=False)
for key, value in topMonthRanked:
    print(key, value)


amounts = [row["amount"] for row in main.values()]

total = sum(amounts)
minimum = min(main.items(), key=lambda pair: pair[1]['amount'])
maximum = max(main.items(), key=lambda pair: pair[1]['amount'])
avg = total / len(amounts)

print()




valid_count = len(main)
invalid_count = len(invalid)
rows_read = valid_count + invalid_count 

dates = [row["date"] for row in main.values()]
earliest = min(dates).strftime("%Y-%m-%d") 
latest = max(dates).strftime("%Y-%m-%d") 
                

def printHeader(fileName) -> str:
    out = f"""SALES REPORT — {fileName}\n{"="*30}"""
    return out
    

def printTotals(rows_read, valid_count, invalid_count, total, avg, minimum, maximum) -> str:
    min_idx, min_row = minimum
    max_idx, max_row = maximum

    out = f"""Rows read:  {rows_read}
Valid:      {valid_count}
Invalid:    {invalid_count}

Revenue total: ${total:,.2f}
Average sale:  ${avg:,.2f}
Min / Max:     ${min_row['amount']:,.2f} (row {min_idx}) / ${max_row['amount']:,.2f} (row {max_idx})"""
    return out


def printProductRanked(ranked, n) -> str:
    lines = ["Top products by revenue"]
    for rank, (name, stats) in enumerate(ranked[:n], start=1):
        lines.append(f"{rank}. {name} ${stats['revenue']:,.2f} ({stats['count']} sales)")
    return '\n'.join(lines)


def printMonthRanked(ranked, earliest, latest) -> str:
    lines = ["Revenue by month"]
    for date, stats in ranked:
        amount_str = f"${stats['revenue']:,.2f}"
        lines.append(f"{date} {amount_str:>12}  ({stats['count']} products sold)")
    lines.append("\n") 
    lines.append(f"Date range: {earliest} .. {latest}")
    return '\n'.join(lines)



def printDataQuality(invalid, negative, duplicates, main) -> str:
    reason_to_field = {"bad amount": "amount", "bad date": "date", "bad product": "product"}
    lines = ["Data Quality"]
    lines.append("  invalid rows")
    for idx, stats in invalid.items():
        for reason in stats["reasons"]:
            field = reason_to_field.get(reason)
            if field is not None:
                row_str = f'("{stats["rowData"][field]}")'
                lines.append(f"     row {idx} {reason:<12}   {row_str:<12}")
            else:
                lines.append(f"     row {idx} {reason}")
    return '\n'.join(lines)


print(printHeader(args.fileName))
print(printTotals(rows_read, valid_count, invalid_count, total, avg, minimum, maximum))
print(printProductRanked(topProductRanked, args.top))
print(printMonthRanked(topMonthRanked, earliest, latest))
print(printDataQuality(invalid, negative, duplicates, main))