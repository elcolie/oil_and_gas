"""Crawl the data from https://www.usagold.com/daily-gold-price-history/"""
import typing as typ
from datetime import datetime

import bs4
import pandas as pd
import requests
from tqdm import tqdm


def crawl(year: int = 1987) -> typ.Tuple[typ.List[datetime], typ.List[float]]:
    """Crawl website and return list."""
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/115.0.0.0 Safari/537.36'}
    url: str = f"https://www.usagold.com/daily-gold-price-history/?ddYears={year}"

    page = requests.get(url, headers=_headers)

    soup = bs4.BeautifulSoup(page.content, "html.parser")
    # print(soup.prettify())
    # Eye ball method found "pricehistorytable"
    table = soup.find(id="pricehistorytable")

    # Iterate through the rows and extract the data
    data = []
    for row in table.find_all("tr"):
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append(cols)

    parsed_data_list: typ.List[typ.Tuple[datetime, float]] = []
    # Clean the data
    for _ in data:
        if _ not in ([], ['']):
            # convert it
            date_string, price_string = _
            format_string: str = "%d %b %Y"
            parsed_date = datetime.strptime(date_string, format_string)
            try:
                price = float(price_string)
            except ValueError:
                price = None
            parsed_data_list.append((parsed_date, price))

    parsed_data_list.reverse()

    # Make datetime column
    dt_column: typ.List[datetime] = [_[0] for _ in parsed_data_list]
    price_column: typ.List[float] = [_[1] for _ in parsed_data_list]
    return dt_column, price_column


def main() -> None:
    """Download data and create gold price CSV file."""
    final_dt_column, final_price_column = [], []
    year_start, year_end = 1987, 2022
    for year in tqdm(range(year_start, year_end + 1, 1)):
        tmp_dt_column, tmp_price_column = crawl(year)
        final_dt_column += tmp_dt_column
        final_price_column += tmp_price_column
    _data: typ.Dict = {"datetime": final_dt_column, "price": final_price_column}
    df = pd.DataFrame.from_dict(_data)
    df.to_csv(f"usagold_{year_start}-{year_end}.csv", index=False)


if __name__ == "__main__":
    main()
