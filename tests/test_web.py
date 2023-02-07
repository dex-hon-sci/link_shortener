#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 21:30:03 2023

@author: dexter
"""
import sys
sys.path.append("../")
import web, main
import pytest

import unittest
from werkzeug import exceptions

# Configurations
from web import app

app.config['TESTING'] = True
app.config['DEBUG'] = False
app.config['WTF_CSRF_ENABLED'] = False

# Define inputs
data = {"URL_original":"https://stackoverflow.com",
                "shortcode":"stack"}
test_url = data['URL_original']
test_shortcode = data['shortcode']

# Other test input
test_shortcode_new = "stack2" #shortcode that does not exist in the database
test_incomplete_url = "stackoverflow.com" #URL that does not have the right format (no https://)

test_db_address = './urls.db'

# Invalid input
empty_url = ""
repeat_shortcode = 'shortcode' # Repeating shortcode in the database
incorrect_char_shortcode = '71%>?' # Illegal characters in shortcode
nonexistent_shortcode = 'nonexistent' # Non-existent shortcode

"""
Test Index page
---------------

"""

# Test for the index page without input
def test_index_get():
    with app.app_context():
        response = app.test_client().get('/')
        
        html_text = open("./template/index2.html").read()
        assert response.status_code == 200 # check connection status
        assert b"Dex link shortener" in response.data 
        
        
# Test for the index page with a valid input url but without shortcode
def test_index_post_valid_empty_shortcode():
    with app.app_context():
        response = app.test_client().post('/', data = {'url':test_url, 'shortcode':""})
        assert response.status_code == 200 # check connection status
        
        # delete the newly added entry for consistency in testing
        #rand_shortcode = main.md5_encoder(test_url)
        #main.URL_DB(rand_shortcode).delete_data_from_db(db_address = test_db_address)
        
# Test for the index page with input url without the prefix "https://" and without shortcode
def test_index_post_incompete_url():
    with app.app_context():
        response = app.test_client().post('/', data = {
            'url':test_incomplete_url, 'shortcode':test_shortcode_new})
        assert response.status_code == 200 # check connection status

        # delete the newly added entry for consistency in testing
        main.URL_DB(test_shortcode_new).delete_data_from_db(db_address = test_db_address)
        
# Test for the index page with a valid input url without shortcode
def test_index_post_valid_given_shortcode():
    with app.app_context():
        response = app.test_client().post('/', data = {
            'url':test_incomplete_url, 'shortcode':""})
        assert response.status_code == 200 # check connection status

        # delete the newly added entry for consistency in testing
        rand_shortcode = main.md5_encoder(test_url)
        main.URL_DB(rand_shortcode).delete_data_from_db(db_address = test_db_address)


"""
Test URL Validity check
-----------------------

"""
# Test for the positive evaluation for validity test
def test_URL_validity_response_positive():
    web_valid = web.URL_valid(test_url,test_shortcode_new,db_address=test_db_address)
    assert web_valid == True
    
    
# Test the URL validity Error messages
class TestsValidityError(unittest.TestCase):  
    
    # Test for the bad request outcome (400)
    def test_URL_validity_response_bad_request(self):
        with self.assertRaises(exceptions.BadRequest): 
            web.URL_valid(empty_url,test_shortcode,db_address=test_db_address)
   
    # Test for conflict outcome (409)
    def test_URL_validity_response_conflict(self):
        with self.assertRaises(exceptions.Conflict):
            web.URL_valid(test_url,repeat_shortcode,db_address=test_db_address) 
   
    # test for precondition fail (412)
    def test_URL_validity_response_precondition_fail(self):
        with self.assertRaises(exceptions.PreconditionFailed):
            web.URL_valid(test_url,incorrect_char_shortcode,db_address=test_db_address)
    
"""
Test Redirection functions
--------------------------

"""

# Test the redirection function        
class TestRedirect(unittest.TestCase):
    
    # end point 302, returns http statuswith the Location header containing the url
    def test_redirect_real_address(self):
        with app.app_context():
            response = app.test_client().get("/stack") # test shortcode "stack"
            assert response.status_code == 302
            
    
    # Test error status 404, Shortcode not found
    def test_redirect_false_address(self):
        with app.app_context():
            response = app.test_client().get("/nonexistent")
            assert response.status_code ==404
            
    # Test error response 404
    def test_redirect_false_address_resp(self):
         with self.assertRaises(exceptions.NotFound): # Raise exception
             web.redirect_URL(nonexistent_shortcode,db_address = test_db_address)
  
"""
Test Stats viewing functions
----------------------------
"""
      
# Test the view stats function   
class TestStats(unittest.TestCase):
    
    # end point 200, return shortcode stats
    def test_shortcode_stats_positive(self):
        with app.app_context():
            response = app.test_client().get("/stack/stats")
            assert response.status_code == 200
            
    # Test error status 404, Shortcode not found
    def test_shortcode_stats_negative(self):
       with app.app_context():
            response = app.test_client().get("/nonexistent/stats")
            assert response.status_code == 404
            
    # Test error response 404
    def test_shortcode_stats_negative_resp(self):
        with self.assertRaises(exceptions.NotFound):
            web.check_shortcode_stats('nonexistent', db_address = test_db_address)
