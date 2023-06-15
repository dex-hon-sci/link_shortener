#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 00:05:55 2023

@author: dexter 
slight changes

"""

from flask import Flask, render_template, redirect, request, \
    abort, jsonify, make_response
import sqlite3
import main

#host = 'https://link-shortener-x4be-master-6vcifd4szq-wm.a.run.app/'
host = 'http://localhost:5000/'
#host = 'http://dex_short.link/'
db_address = './urls.db'

app = Flask(__name__, template_folder='template')

base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # url input
        url = request.form['url']
        
        # replace white space with blanks
        shortcode = request.form['shortcode'].replace(" ", "") 
        
        # Check if URL and shortcode input are valid 
        validity = URL_valid(url, shortcode)

        # If the inputs are valid, attempt to either save or create a shortcode
        if validity == True:
            ## check if the url leads with "http://"
            if "http" in url[0:7]:
                pass
            else:
                url = "https://"+url #add it to the string
            #else: 
            #    pass
            
            if shortcode == "":
                # Generate a 6 digit string if the input shortcode is empty
                shortcode = main.md5_encoder(url)                
                
                # Check again if the 6 digit code is already in the database
                shortcode_list = main.URL_DB(shortcode).fetch_data_from_db(db_address=db_address)
                
                # In the case that the shortcode does not exist in the database
                if len(shortcode_list) ==0:
                    # add the shortcode to the database
                    main.URL_DB(shortcode).add_data_to_db(url, db_address =db_address)
                
                # In the case that the shortcode already exists in the database
                elif len(shortcode_list) > 0:
                    pass
            else:
                main.URL_DB(shortcode).add_data_to_db(url)

            # make a new shorten url
            short_url = host + shortcode
            
            #make the stats page
            stats_page = host+shortcode+"/stats"
        #else: 
        #    pass

        # The default output response 
        response = render_template('index2.html',short_url=short_url, 
                            stats_page=stats_page)
        
        pack = jsonify(shortcode=shortcode)

        # I added 'response2' because the question asked me to return status 201
        # with the shortcode as the output. I prefer 'response' instead.
        response2 = make_response(pack)
        return response
    return render_template('index2.html')       

    
def URL_valid(url,shortcode,db_address=db_address):
    """
    A function to check if the input URL and shortcode are valid.

    Parameters
    ----------
    url : str
        The original URL.
    shortcode : str
        The given shortcode by users.

    Returns
    -------
    If the URL input is not present, return error page 400.
    If the shortcode is already in use, return error page 409.
    If the shortcode is not in the database, return error page 412.
    Otherwise, return True.

    """
    # Connect to databse
    conn = sqlite3.connect(db_address)
    cur = conn.cursor()
    res = cur.execute("SELECT shortcode FROM WEB_URL")

    shortcode_list = res.fetchall()
    # Check for errorneous inputs
    
    # return 400 error page if URL is not present
    if url == "":     
        message = "Status 400. Empty input is not acceptable."
        return abort(400, message)
        #return abort(make_response(jsonify(message=message)),400)
    
    # return 409 error page if shortcode is already in use
    elif (shortcode,) in shortcode_list: 
        message = 'Status 409. Shortcode is already in use. Please choose another one.'
        return abort(409, message)
        #return abort(make_response(jsonify(message=message)),409)
    else:
        pass
    # return 412 error page if provided shortcode is invalid   
    # loop through the shortcode to check for illegal characters
    for i in range(len(shortcode)):
        if shortcode[i] not in base:
            message = """Status 412. Illegal characters detected in the shortcode. 
                         Only 0-9,a-z, and A-Z are allowed."""
            return abort(412, message)
            #return abort(make_response(jsonify(message=message)),412)
       # else:
       #     pass
    return True
    
@app.route('/<shortcode>',methods=['GET'])
def redirect_URL(shortcode,db_address =db_address):
    """
    Redirect using a given shortcode.
    The function look up the database to fetch the original URL using a 
    given shortcode. It redirects the webpage to that URL.

    Parameters
    ----------
    shortcode : str
        The given shortcode inout by the users.

    Returns
    -------
    TYPE
        Redirect to the original URL.

    """
    #open up database
    conn = sqlite3.connect(db_address)
    cur = conn.cursor()
    
    res = cur.execute("SELECT shortcode FROM WEB_URL")
    
    # save the master list of shortcode
    bag = res.fetchall()
    
    # check if the shortcode exist
    if (shortcode,) in bag:
        #fetch long url, then redirect    
        res= cur.execute("SELECT URL_original FROM WEB_URL WHERE shortcode=?",
                         (shortcode,))
        url = res.fetchall()[0][0]

        # update statistic
        main.URL_DB(shortcode).update_redirect_record()
        
        response = make_response(redirect(url,code=302))

        return response
           
    else:
        return abort(404)

@app.route('/<shortcode>/stats',methods=['GET'])
def check_shortcode_stats(shortcode, db_address = db_address):
    """
    To view the statistics of a given shortcode.

    Parameters
    ----------
    shortcode : str
        The given shortcode inout by the users.

    Returns
    -------
    Redirect to a page that contains the json file with the following info:
        { "created": datetime of the entry creation,
         "lastRedirect": datetime of the last redirection,
         ""redirectCount": the number of time this shorten link have been used."}
    """
    #open up database
    conn = sqlite3.connect(db_address)
    cur = conn.cursor()
    
    res = cur.execute("SELECT shortcode FROM WEB_URL")
    
    # save the master list of shortcode
    bag = res.fetchall()

    if (shortcode,) not in bag:
        return abort(404, "Shortcode not found in the database.")
    else:
        # fetch the data entry from a given shortcode
        val = main.URL_DB(shortcode).fetch_data_from_db()

        # make Json file output that contain the stats for a given shortcode
        pack = jsonify(created=val[0][-3], 
                       lastRedirect=val[0][-2],
                       redirectCount=val[0][-1])
        response = make_response(pack)
        return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
