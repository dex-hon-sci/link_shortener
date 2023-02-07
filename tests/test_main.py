#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 20:07:02 2023

@author: dexter
"""
#import sys
#sys.path.append("../")

import main
import os.path
import sqlite3
"""
Test encoding
"""
# what happens if someone define a shortcode that is exactly the same as the md5 shortcode
def test_md5_encoder_default() -> None:
    shortcode = main.md5_encoder("http://stackoverflow.com")
    assert shortcode == '6feb5a'

# check the encoding
def test_md5_encoder() -> None:
    shortcode = main.md5_encoder("google.com")
    assert shortcode == '536f5a'
    
# Check the length of the encoding product
def test_md5_encoder_length() -> None:
    shortcode = main.md5_encoder("gabrbdsb")
    assert len(shortcode) == 6
    
# test if the random string is generated using the base string
def test_random_string_type() -> None:
    base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    shortcode = main.random_string()
    shortcode_list = [shortcode[i] for i in range(len(shortcode))] 
    
    for i in range(len(shortcode_list)):
        assert shortcode_list[i] in base
        
# Check the length customisation of randomvstring        
def test_random_string_length() -> None:
    shortcode = main.random_string(length=10)
    assert len(shortcode) == 10

# Check if shortcode can be called (empty case)
def test_DB_empty_shortcode() -> None:
    assert main.URL_DB().shortcode == ""

# Check if shortcode can be called
def test_DB_shortcode() -> None:
    assert main.URL_DB("long").shortcode == "long"

def test_DB_create_table() -> None:
    main.URL_DB().create_table(db_address ="./test_create_urls.db")
    assert os.path.exists("./test_create_urls.db") == True
    os.remove("./test_create_urls.db") #delete the file
    
# Check if the fetch function works using the test entry (first entry) in the database 
def test_fetch_from_DB() -> None:
    #fetch the first entry
    val = main.URL_DB("shortcode").fetch_data_from_db(db_address= './test_urls.db')
    answer = [(1, 'URL', 'shortcode', 'create_datetime', 'last_redirect', 0)]
    assert val == answer
    
# Check if the fetch function works a non-existent shortcode     
def test_fetch_from_DB_wrong_shortcode() -> None:
    # try non-existent shortcode, assuming "nonExistent" is not used as shortcode
    val = main.URL_DB("nonExistent").fetch_data_from_db(db_address= './test_urls.db')
    assert val == []

"""
Test database operations
"""
# input data 
index = sqlite3.connect(
        'test_urls.db').cursor().execute(
            """ SELECT id FROM WEB_URL""").fetchall()[-1][0] +1
URL = "http://example.com"
shortcode = "testshortcode"
last_redirect = ""
redirect_count = 0
db_address = './test_urls.db' 
        
# Test the add function in the database
def test_add_data_to_DB_default() -> None:
    
    # add the new entry to the database.
    main.URL_DB(shortcode).add_data_to_db(URL, db_address= db_address)  
    
    # reference info for the input entry.
    # The creation time has to be fetched instead of generated, or else there  
    # will be a fractional difference in time.
    creation_datetime = main.URL_DB(
        shortcode).fetch_data_from_db(db_address= db_address)[0][3]

    # the input data
    input_data = [(index, URL, shortcode,creation_datetime,last_redirect,redirect_count)]
    
    # fetch the new entry
    val =  main.URL_DB(shortcode).fetch_data_from_db(db_address= db_address)
    
    assert input_data == val
    
# Test the update function
def test_update_redirect_record() -> None: 
    # Update the redirect reocrd
    main.URL_DB(shortcode).update_redirect_record(db_address=db_address)

    val =  sqlite3.connect(db_address).cursor(
            ).execute(
                "SELECT * FROM WEB_URL WHERE shortcode=?", [str(shortcode)]).fetchall()
                
    # Fetch the datetime and redirect datetime
    creation_datetime = main.URL_DB(
        shortcode).fetch_data_from_db(db_address= db_address)[0][3]
    last_redirect = main.URL_DB(
        shortcode).fetch_data_from_db(db_address= db_address)[0][4]
    

    answer = [(index, URL, shortcode, creation_datetime, last_redirect, 1)]
    
    assert val == answer

# Test the delete function
def test_delete_data_from_DB_default() -> None:
    # Delete all entry with shortcode = 'test_shortcode'
    main.URL_DB(shortcode).delete_data_from_db(db_address= db_address)
    
    val =  sqlite3.connect(db_address).cursor(
        ).execute("SELECT * FROM WEB_URL").fetchall()
    
    answer = [(1, 'URL', 'shortcode', 'create_datetime', 'last_redirect', 0)]

    # Assume after deletion, the only thing left is the test entry
    assert val == answer
