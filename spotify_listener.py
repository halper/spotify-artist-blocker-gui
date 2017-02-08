#!/usr/bin/python
#coding: utf-8
 
from subprocess import PIPE
from subprocess import call
from time import strftime
import subprocess, time, MySQLdb
import json,urllib,re
api_key=''
database = ''
user = ''
pwd = ''

def getGenreID(cursor, tags):
    cursor.execute("""SELECT * FROM genres""")
    for row in cursor:
        g_id = row[0]
        g_name = row[1]
        for i in range(0, len(tags)):
            if g_name.lower() in tags[i]['name'].lower():
                return g_id
    return ''
                
def getTags(artist, title):
    json_url='http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key='+api_key+'&artist='+artist+'&track='+title+'&format=json'
    try:
        data = urllib.urlopen(json_url).read().decode("utf-8")
        output = json.loads(data)
        if 'error' in output:
            print 'Error: ' + output['message']
            return ""
        else:
            return output['track']['toptags']['tag']
    except ValueError:
        print "JSON object related error"
        return ""

    
def handleDBOps(trackid, cover, album, artist, title, duration):
    # Open database connection
    db = MySQLdb.connect("localhost", user, pwd, database, use_unicode=True, charset="utf8" )
    cursor = db.cursor()
    
    tags = getTags(artist, title)
    genre_id = getGenreID(cursor, tags)
    genre_id = '10' if not genre_id else genre_id

    # execute SQL query using execute() method.
    cursor.execute("""SELECT COUNT(*) FROM songs WHERE trackid = %s""", [trackid])

    # Fetch a single row using fetchone() method.
    result = cursor.fetchone()
    now = strftime("%Y-%m-%d %H:%M:%S")
    if int(result[0]) > 0:
        try:
            cursor.execute("""UPDATE songs SET played = %s, played_on = %s, duration = %s WHERE trackid = %s""", [int(result[0])+1, now, duration, trackid])
            db.commit()
        except:
            db.rollback()
    else:
        try:
            cursor.execute("""INSERT INTO songs (trackid, cover, album, artist, title, genre_id, duration, played_on) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", [trackid, cover, album, artist, title, genre_id, duration, now])
            db.commit()
        except MySQLdb.Error, e:
            try:
                print "genre_id: %s \nMySQL Error [%d]: %s" % (genre_id, e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)
            db.rollback()
        
    # disconnect from server
    db.close()
    
def getRestrictedArtists():
    db = MySQLdb.connect("localhost", user, pwd, database )
    cursor = db.cursor()
    cursor.execute("""SELECT artist FROM songs WHERE restricted=1""")
    my_list = []
    for row in cursor:
        my_list.append(row[0])
    db.close()
    return my_list

def playNextSong():
    cmd = ["dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Next"]
    s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout

cmd = ['dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:"org.mpris.MediaPlayer2.Player" string:"Metadata"']
previously_playing = ''
while(1):
    songHasChanged = ''
    s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
    service_state = s.read().splitlines()
    i = 0
    artist = ''
    cover = ''
    album = ''
    title = ''
    duration = ''
    trackid = ''

    for line in service_state:
        if 'artUrl' in line:
            cover = (service_state[i+1].split('"')[1::2])[0].split('/')[-1]
        if 'trackid' in line:
            trackid = (service_state[i+1].split('"')[1::2])[0].split(':')[-1]
        if 'album"' in line:
            album = (service_state[i+1].split('"')[1::2])[0]
        if 'artist"' in line:
            artist = (service_state[i+2].split('"')[1::2])[0].lower()
        if 'title' in line:
            title = (service_state[i+1].split('"')[1::2])[0].lower()
        if 'length"' in line:
            duration = (service_state[i+1].split(' ')[-1])
        i += 1
        
    restrictedArtistsList = getRestrictedArtists()
    if artist in restrictedArtistsList:
        playNextSong()
        songHasChanged = True
    currently_playing = artist + ' - ' + title
    if not previously_playing or not (previously_playing.lower() in currently_playing.lower()):
        previously_playing = currently_playing
        if not 'spotify' in currently_playing:
            print currently_playing
            handleDBOps(trackid, cover, album, artist, title, duration)
    if not songHasChanged:
        time.sleep(15)



