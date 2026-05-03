import requests
from bs4 import BeautifulSoup, Tag


def fetch_top_100_apps():
    """
    Fetch top 100 grossing Google Play apps from AppBrain.

    Returns:
        list[dict]: Each item contains rank, app_id, app_name, developer, and category.
    """

    url = "https://www.appbrain.com/stats/google-play-rankings/top_grossing/all/us"

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        ranking_table = soup.find("table", id="rankings-table")

        if not ranking_table:
            return []

        tbody = ranking_table.find("tbody")

        if not tbody:
            return []

        app_list = []
        rank = 0

        for tr in tbody.children:
            if not isinstance(tr, Tag):
                continue

            app_cell = tr.find("td", class_="ranking-app-cell")

            if not app_cell:
                continue

            app_links = app_cell.find_all("a")

            if len(app_links) < 2:
                continue

            rank += 1

            app_link = app_links[0].get("href", "")
            app_id = app_link.split("/")[-1]
            app_name = app_links[0].text.strip()

            developer_link = app_links[1].get("href", "")
            developer_name = app_links[1].text.strip()

            category_cell = app_cell.find_next_sibling("td")

            if category_cell and category_cell.find("a"):
                category_link = category_cell.find("a").get("href", "")
                category_name = category_cell.find("a").text.strip()
            else:
                category_link = ""
                category_name = ""

            app_list.append({
                "rank": rank,
                "app_id": app_id,
                "app_name": app_name,
                "developer": developer_name,
                "developer_link": developer_link,
                "category": category_name,
                "category_link": category_link
            })

            if rank >= 100:
                break

        return app_list

    except requests.RequestException as e:
        print(f"Error fetching AppBrain ranking page: {e}")
        return []