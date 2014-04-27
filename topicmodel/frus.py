"""
Make OOP
Make replicable
Make module for topic modelling, so we can plug in 
either FRUS or Sasha's text predictions
"""
import redact.data.passwd as passwd


def get_frus(n):
    """Establish database connection and 
    perform query to fetch rows
    
    Parameters
    ----------
    n : the number of rows to fetch
    
    Returns
    -------
    cursor : pointer to the DB
    """    
    db = passwd.get_db()
    cursor = passwd.get_cursor(db)
    q = "select * from frus limit 1000"
    cursor.execute(q)
    return cursor

def get_text(cursor):
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


