#!/usr/bin/python

import  requests, re
from    bs4 import BeautifulSoup
import argparse
import MySQLdb
import sys

def get_urls(search_string, start, db, cursor, table):
    url         = 'http://www.google.com/search'
    payload     = { 'q' : search_string, 'start' : start }
    my_headers  = { 'User-agent' : 'Mozilla/11.0' }
    r           = requests.get( url, params = payload, headers = my_headers )
    soup        = BeautifulSoup( r.text, 'html.parser' )
    h3tags      = soup.find_all( 'h3', class_='r' )
    for h3 in h3tags:
        try:
            url = re.search('url\?q=(.+?)\&sa', h3.a['href']).group(1)
            cursor.execute("INSERT INTO " + table + " (url) VALUES ('" + url + "')")
            db.commit()
        except:
            db.rollback()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--number', '-n', required=True, help='Number of pages')
    parser.add_argument('--search', '-s' ,required=True, help='Search string')
    parser.add_argument('--addr', '-a', default='localhost', help='Server addr (Default=localhost)')
    parser.add_argument('--database', '-d' ,default='dork', help='DB name (Default=dork)')
    parser.add_argument('--user', '-u' ,required=True, help='Username')
    parser.add_argument('--table', '-t' ,required=True, help='Table name')
    parser.add_argument('--password', '-p' ,required=True, help='Database password')
    args = parser.parse_args()

    try:
        db = MySQLdb.connect(args.addr,
                         user=args.user,
                         passwd=args.password,
                         db=args.database)
    except:
        print("Access denied")
        sys.exit()

    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS " + args.table + " (id INT NOT NULL AUTO_INCREMENT, url TEXT NOT NULL, checked TINYINT(1) DEFAULT 0, PRIMARY KEY (id))")

    for page in range( 0,  int(args.number) ):
        get_urls(args.search, str(page*10),db , cur, args.table) 

    cur.close()
    db.close()

if __name__ == '__main__':
    main()
