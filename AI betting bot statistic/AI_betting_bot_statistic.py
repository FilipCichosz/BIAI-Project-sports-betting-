# code is structured to run also in colab/jupyterLab and get the view of data on every step of scraping and editing, to make wanted adjustment to your project
import requests

standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"  #To scrape other league the PL en change the link to correct link of leauge you are intrested, make sure to that below too

data = requests.get(standings_url)

from bs4 import BeautifulSoup

soup = BeautifulSoup(data.text)
standings_table = soup.select('table.stats_table')[0]
links = standings_table.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if '/squads/' in l]

team_urls = [f"https://fbref.com{l}" for l in links]

data = requests.get(team_urls[0])

import pandas as pd
matches = pd.read_html(data.text, match="Scores & Fixtures")[0]

soup = BeautifulSoup(data.text)
links = soup.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if l and 'all_comps/shooting/' in l]

data = requests.get(f"https://fbref.com{links[0]}")

shooting = pd.read_html(data.text, match="Shooting")[0]

shooting.head()

shooting.columns = shooting.columns.droplevel()

team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")

team_data.head()

years = list(range(2024, 2022, -1)) #Years of season we are intrested in from 2 to 4 is a sweat-spot, because data on wider time span is not so relevant
all_matches = []
standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats" 

import time
for year in years:
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text)
    standings_table = soup.select('table.stats_table')[0]

    links = [l.get("href") for l in standings_table.find_all('a')]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]
    
    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}"
    
    for team_url in team_urls:
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
        data = requests.get(team_url)
        matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
        soup = BeautifulSoup(data.text)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/shooting/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        shooting = pd.read_html(data.text, match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel()
        try:
            team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
        except ValueError:
            continue
        team_data = team_data[team_data["Comp"] == "Premier League"]
        
        team_data["Season"] = year
        team_data["Team"] = team_name
        all_matches.append(team_data)
        time.sleep(6) #on/below 5 fbref or sofascore gives timeout on read through soup

len(all_matches)
match_df = pd.concat(all_matches)
match_df.columns = [c.lower() for c in match_df.columns]
match_df
match_df.to_csv("matches.csv")