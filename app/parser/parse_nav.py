import pandas as pd
import re
import chardet


def parse_nav_file(file_path):
    with open(file_path, 'rb') as raw:
        raw_data = raw.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding'] or 'latin1'

    lines = raw_data.decode(encoding, errors='replace').splitlines()

    data = []
    scheme_type = scheme_category = scheme_sub_category = fund_structure = ""
    fund_house = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ';' not in line:
            if line.startswith("Open Ended") or line.startswith("Close Ended"):
                scheme_type = line
                scheme_category = scheme_sub_category = ""
            elif "Fund" in line:
                fund_house = line
            continue
        parts = line.split(';')
        if len(parts) == 8:
            scheme_code, scheme_name, isin_growth, isin_reinv, nav, repurchase, sale, nav_date = parts
            data.append([
                scheme_type,
                scheme_category,
                scheme_sub_category,
                scheme_code,
                isin_growth,
                isin_reinv,
                scheme_name,
                nav,
                nav_date,
                fund_house
            ])

    df = pd.DataFrame.from_records(data, columns=[
        "Scheme Type",
        "Scheme Category",
        "Scheme Sub-Category",
        "Scheme Code",
        "ISIN Div Payout/ISIN Growth",
        "ISIN Div Reinvestment",
        "Scheme Name",
        "Net Asset Value",
        "Date",
        "Fund Structure"
    ])
    return df
