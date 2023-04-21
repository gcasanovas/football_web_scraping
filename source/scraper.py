import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import sys, getopt
import csv
import random
import urllib.robotparser as urobot
import lxml
import datetime
import warnings
import logging

logging.basicConfig(level=logging.DEBUG)


class LeaguesScraper:
    def __init__(self, url):
        self.url = url
        self.user_agents_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
             Chrome/111.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
             Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46'
        ]
        self.global_table_cols = [
            "team", "games", "points", "wins", "ties", "losses", "goals_for", "goals_against", "goal_diff", "xg_for",
            "xg_against", "xg_diff"
        ]
        self.team_stats_table_cols = [
            "team", "players_used", "avg_age", "possession", "games", "games_starts", "minutes", "minutes_90s",
            "assists", "goals_assists", "goals_pens", "pens_made", "pens_att", "cards_yellow", "cards_red"
        ]

    def _get_header(self):
        """Creates a header for a http request to prevent the website from detecting us using web scraping"""
        user_agent = [random.randrange(len(self.user_agents_list))]
        return {'User-Agent': user_agent}

    def _check_robots_file(self, ignore=0):
        """Checks the website's robots.txt for web scraping restrictions"""
        logging.info(f'Checking crawling restrictions for website: {self.url}')
        rp = urobot.RobotFileParser()
        rp.set_url(self.url + '/robots.txt')
        rp.read()
        if rp.can_fetch('*', self.url):
            logging.info('Crawling allowed')
        else:
            if ignore == 1:
                warnings.warn('Crawling not allowed')
            else:
                raise SystemExit('Crawling not allowed, to crawl anyway set ignore=1')

    def _make_soup(self):
        """Makes http request, get html contents, deletes comments and returns tables stored under tbody tags"""
        logging.info(f'Getting data from website: {self.url}')
        try:
            # Make http request changing user-agent
            content = requests.get(self.url, self._get_header(), timeout=10)
        except requests.exceptions.Timeout:
            raise SystemExit('The server is not available, try again later')
        # Create soup while removing html comments
        comm = re.compile("")
        soup = BeautifulSoup(comm.sub("", content.text), 'lxml')
        # Find tables
        tables = soup.findAll("tbody")
        return tables

    def _get_global_table(self, table):
        """Returns a dataframe with global_table data"""
        df = dict()
        logging.info(f'Parsing data for global_table from website: {self.url}')
        rows = table.find_all('tr')
        for row in rows:
            if row.find('th', {"scope": "row"}) is not None:
                for col in self.global_table_cols:
                    register = row.find('td', {"data-stat": col}).text.strip().encode().decode("utf-8")
                    if col in df:
                        df[col].append(register)
                    else:
                        df[col] = [register]
        return pd.DataFrame.from_dict(df)

    def _get_teams_stats_table(self, table):
        """Returns a dataframe with teams_stats_table data"""
        df = dict()
        logging.info(f'Parsing data for teams_stats_table from website: {self.url}')
        rows = table.find_all('tr')
        for row in rows:
            if row.find('th', {"scope": "row"}) is not None:
                for col in self.team_stats_table_cols:
                    if col == 'team':
                        register = row.find('th', {"data-stat": col}).text.strip().encode().decode("utf-8")
                    else:
                        register = row.find('td', {"data-stat": col}).text.strip().encode().decode("utf-8")
                    if col in df:
                        df[col].append(register)
                    else:
                        df[col] = [register]
        return pd.DataFrame.from_dict(df)

    def _save_results_to_csv(self, df):
        """Saves results inside data directory as csv files"""
        league_name = re.search(r'-de-(.+)', self.url).group(1)
        csv_filepath = f'data/final_table_{league_name}_{datetime.datetime.now().strftime("%Y_%m_%d")}'\
            .replace('-', '_').lower()
        logging.info(f'Saving data to: {csv_filepath}')
        df.to_csv(csv_filepath, index=False)

    def scrape(self, ignore=0):
        # Check if website can be crawled
        self._check_robots_file(ignore=ignore)
        # Make http request and get tables from website
        tables = self._make_soup()
        # Parse data for global_table
        global_table = self._get_global_table(tables[0])
        # Parse data for teams_stats_table
        teams_stats_table = self._get_teams_stats_table(tables[2])
        # Merge tables into one
        merged_df = pd.merge(global_table, teams_stats_table, how='inner', on='team', suffixes=(None, '_y'))
        columns = [col for col in merged_df.columns if not col.endswith('_y')]
        final_table = merged_df[columns]
        # Save results to csv
        self._save_results_to_csv(df=final_table)

