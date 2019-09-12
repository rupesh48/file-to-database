#This application will read an iTunes export file in XML and produce a properly normalized database with this structure:
#If you run the program multiple times in testing or with different files, make sure to empty out the data before each run.

#The ZIP file contains the Library.xml file
#You can export your own tracks from iTunes and create a database.

#SELECT Track.title, Artist.name, Album.title, Genre.name 
#    FROM Track JOIN Genre JOIN Album JOIN Artist 
#    ON Track.genre_id = Genre.ID and Track.album_id = Album.id 
#       AND Album.artist_id = Artist.id
#    ORDER BY Artist.name LIMIT 3
#The expected result of the modified query on your database is: (shown here as a simple HTML table with titles)

#Track	                                    Artist	Album	        Genre
#Chase the Ace	                            AC/DC	Who Made Who	Rock
#D.T.	                                    AC/DC	Who Made Who	Rock
#For Those About To Rock (We Salute You)	AC/DC	Who Made Who	Rock


import xml.etree.ElementTree as ET 
import sqlite3

conn=sqlite3.connect('db.sqlite')
cur=conn.cursor()

cur.executescript('''
    drop table if exists artist;
    drop table if exists genre;
    drop table if exists album;
    drop table if exists track;
    
    create table artist(
        id integer not Null primary key autoincrement unique,
        name text unique);
        
    create table genre(
        id integer not Null primary key autoincrement unique,
        name text unique);
        
    create table album(
        id integer not Null primary key autoincrement unique,
        artist_id integer,
        title text unique);
        
    create table track(
        id integer not Null primary key autoincrement unique,
        title text unique,
        album_id integer,
        genre_id integer,
        len integer, rating integer,count integer
        );
        ''')
        
fname= input('Enter file name : ')
if(len(fname)<1): fname='Library.xml'

def lookup(k,key):
    found=False
    for child in k:
        if found: return child.text
        if child.tag=='key' and child.text==key:
            found=True
    return None
    
stuff=ET.parse(fname)
all=stuff.findall('dict/dict/dict')
print('Dict count:',len(all))
for entry in all:
    if(lookup(entry,'Track ID')is None):
        continue
    name=lookup(entry,'Name')
    artist=lookup(entry,'Artist')
    album=lookup(entry,'Album')
    genre=lookup(entry,'Genre')
    count=lookup(entry,'Play Count')
    rating=lookup(entry,'Rating')
    length=lookup(entry,'Total Time')
    
    if name is None or artist is None or album is None or genre is None:
        continue
        
    print(name,artist,album,genre,count,rating,length)
    
    cur.execute('insert or ignore into artist(name) values(?)',(artist,))
    cur.execute('select id from artist where name=?',(artist,))
    artist_id =cur.fetchone()[0]
    
    cur.execute('insert or ignore into genre(name) values(?)',(genre,))
    cur.execute('select id from genre where name=?',(genre,))
    genre_id =cur.fetchone()[0]
    
    cur.execute('insert or ignore into album(title,artist_id) values(?,?)',(album,artist_id))
    cur.execute('select id from album where title=?',(album,))
    album_id =cur.fetchone()[0]
    
    cur.execute('insert or replace into track(title,album_id,genre_id,len,rating,count) values(?,?,?,?,?,?)',(name,album_id,genre_id,length,rating,count))
    conn.commit()