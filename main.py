from scrapper import Scraper
from database_transfer import send_to_database
import pandas as pd
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('logs.log')
formattor = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formattor)
logger.addHandler(handler)


creds = pd.read_csv('creds.csv')  # please first set your credentials in creds.csv
id, pw = creds.iloc[0,:].values

s1 = Scraper(id, pw)
s1.login()

try:
    data = s1.run(query = "Amazon SDE", pages = 2)
except:
    logger.exception("Robo Wall Detected")
    _ = input("Once you clear the robo wall puzzle, respond? (done)")
    data = s1.run(query = 'Amazon SDE', pages = 2)


send_to_database(data)