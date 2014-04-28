"""
Make OOP
Make replicable
Make module for topic modelling, so we can plug in 
either FRUS or Sasha's text predictions
"""
import redact.data.passwd as passwd
import re

def get_texts(n):
    """Establish database connection and 
    perform query to fetch rows
    
    Parameters
    ----------
    n : the number of documents to fetch
    
    Returns
    -------
    cursor : pointer to the DB
    """    
    db = passwd.get_db()
    cursor = passwd.get_cursor(db)
    q = "select fullbody from frus limit " + str(n) 
    cursor.execute(q)
    all_texts = [row['fullbody'] for row in cursor]

    return all_texts

def get_redactions(all_texts):
    # Format: list of lists, list per document of redactions
    redact = [re.findall("\[.*?declassified.*?\]", text) \
            for text in all_texts]
    return redact

def get_indices(all_texts):
    # Indices of redactions
    indices = [re.finditer("\[.*?declassified.*?\]", text) \
            for text in all_texts]

def get_para(all_texts):
    # Get the paragraph surrounding the redaction 
    # including the redaction marking.
    # returns lists of list per document
    para = [re.findall("\n(.*?\[.*?declassified.*?\].*?)\n", text) \
            for text in all_texts]
    return para

def get_surround(all_para):
    # Note that this also flattens the list, 
    # Now it's a list of strings not of lists.
    surr = [re.sub("\[.*?declassified.*?\]", "", p) \
            for doc in all_para \
            for p in doc]
    return surr

