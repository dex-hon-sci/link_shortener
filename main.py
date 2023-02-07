#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 08:22:57 2023

@author: dexter
"""

import sqlite3
import datetime
import random
import hashlib 

host = 'http://localhost:5000/'

host_name='/dex_short.lnk/'


def md5_encoder(url):
    """
    Base 36 encoder

    Generate unique short url link.

    Parameters
    ----------
    url: str
        Long url string.

    Returns
    -------
    Shortcode.

    """    
    # Generate hash code based on input link
    hash_code = hashlib.md5(url.encode())
    
    # Choose the last 6 digits of the hash code
    # The amount to 1,073,741,824 possibilities
    target_url = hash_code.hexdigest()[-6:]
            
    return target_url

def random_string(length:int=6):
    """
    Generate a random x-digits alphanumerical string

    Parameters
    ----------
    length : int
        The number of digits.

    Returns
    -------
    Shortcode.

    """
    base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # Pick a random 6 digits string from base
    # The amount to 56,800,235,584 possibilities
    code = ''.join([random.choice(base) for i in range(length)])

    return code

class URL_DB(object):
    """
    Description
    -----------
    The :class: that manage and manipulate the database for the URL shortener
    webservice.
    """
    def __init__(self, shortcode=""):
        """
        Initialize an instance of the :class:`URL_DB` class.

        Parameters
        ----------
        shortcode : str, optional
            The inserted input of the shortcode. This code is an unique 
            identifier (aside from 'id') in the database.
            The default is "".

        """
        self.shortcode = shortcode 
    
    def create_table(self, db_address ="./urls.db"):
        """
        Creating a table. To be used only once.


        """
        create_table = """CREATE TABLE WEB_URL(id, 
                                            URL_original, 
                                            shortcode, 
                                            create_datetime, 
                                            last_redirect,    
                                            redirect_count)"""
        # Insert reference entry
        first_entry = """INSERT INTO WEB_URL VALUES(
                                        1, "URL","shortcode",
                                        "create_datetime","last_redirect",0) """
        
        # Connect to a new database
        conn = sqlite3.connect(db_address) 
        cursor = conn.cursor()
        # create table
        cursor.execute(create_table)
        
        # Insert first entry that is blank
        cursor.execute(first_entry)
        conn.commit()
        return "NEW TABLE!!"


    def fetch_data_from_db(self,  db_address ="./urls.db"):
        """
        Fetch data from the database with a given shortcode.

        Returns
        -------
        val : list
            A list that contain all info associated with the shortcode.

        """
        conn = sqlite3.connect(db_address)
        cur = conn.cursor()
        
        data = [str(self.shortcode)]
                
        res = cur.execute("SELECT * FROM WEB_URL WHERE shortcode=?",data)
        val = res.fetchall()
        return  val 
          
    def add_data_to_db(self, url, db_address ="./urls.db"):
        """
        Add data to the database.
        
        Parameters
        ----------
        url : str, 
            The original URL input. 
        """
        # Connect to database
        conn = sqlite3.connect(db_address)
        cur = conn.cursor()
        
        # Read the id list of the database
        res = cur.execute("SELECT * FROM WEB_URL")
        
        # add one to the length of the existing fatabase
        index = len(res.fetchall())+1 

        creation_datetime = datetime.datetime.utcnow().isoformat()
        last_redirect = ""
        redirect_count = 0
        
        # input data
        data = [(index, str(url), str(self.shortcode), creation_datetime,
                 last_redirect, redirect_count)]
    
        cur.executemany("INSERT INTO WEB_URL VALUES(?, ?, ?, ?, ?, ?)", data)
        conn.commit()
        return "New entry added"
    
    def delete_data_from_db(self, db_address ="./urls.db"):
        """
        Delete all entries with a given shortcode.

        """
        conn = sqlite3.connect(db_address)
        cur = conn.cursor()
        
        cur.execute("DELETE FROM WEB_URL WHERE shortcode=?",
                    [str(self.shortcode)])
        conn.commit() 
        
        return "Deleted!"
    
    def update_redirect_record(self, db_address ="./urls.db"):
        """
        Update the redirect record in the database.

        """
        conn = sqlite3.connect(db_address)
        cur = conn.cursor()
        
        old_fetch_count = cur.execute("SELECT redirect_count FROM WEB_URL \
                                      WHERE shortcode=?", 
                                      [str(self.shortcode)]).fetchall()
        
        # fetch time 
        fetch_time = datetime.datetime.utcnow().isoformat()
        fetch_count = old_fetch_count[0][0] + 1
        
        # update data
        data = [fetch_time, fetch_count, self.shortcode]
        
        statement = """UPDATE WEB_URL 
                          SET last_redirect="{}" , 
                              redirect_count ={} 
                          WHERE shortcode ="{}"
                          """.format(str(data[0]), str(data[1]), data[2])
                          
        cur.execute(statement)
        conn.commit()

        return "Updated!"