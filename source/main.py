from scraper import LeaguesScraper


if __name__ == '__main__':

    urls = ['https://fbref.com/es/comps/12/Estadisticas-de-La-Liga',
            'https://fbref.com/es/comps/9/Estadisticas-de-Premier-League',
            'https://fbref.com/es/comps/11/Estadisticas-de-Serie-A',
            'https://fbref.com/es/comps/20/Estadisticas-de-Bundesliga',
            'https://fbref.com/es/comps/13/Estadisticas-de-Ligue-1']

    try:
        for url in urls:
            scraper = LeaguesScraper(url=url)
            scraper.scrape()
    except Exception as e:
        print(f'Error: {e}')
