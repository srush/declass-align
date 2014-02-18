"""
Class for managing and retrieving DDRS documents.
"""

import re  

class Document:
  def __init__(self, row, prefix = ""):
      """
      Create a Document from a database row.

      """
      self.prefix = prefix
      self.row = row
      t2 = self._get_row("body")
      text = re.sub("<\?HR\?>(.)*?<\?PRE\?>", "<?PRE?>", self._get_row("body"))
      text = re.sub("<\?HR\?>(.)*?</DOC\.BODY>", "</DOC.BODY>", text)
      text = text.strip("\"")
      
      self.text = text.replace("</PARA>", " "). \
          replace("<PARA>", " ") \
          .replace("<?BR?>", " ") \
          .replace("<?PRE?>", " <?PRE?> "). \
          replace("<?HR?>", " "). \
          replace("</DOC.BODY>", " "). \
          replace("<DOC.BODY>", " "). \
          replace("\\n", " ")
      
      self.id = self._get_row("id")
      self.title = self._get_row("title")
      self.date = self._get_row("written")

  def _get_row(self, name):
      "Returns the column indicated by name."
      return self.row[self.prefix + name]


  @staticmethod
  def from_id(cursor, doc_id):
      """
      Get a document by its id.
      
      cursor: 
         DB cursor.
      
      doc_id:
         A document id. 
      """
      query = "select * from Document where id = %s"
      cursor.execute(query, doc_id)
      doc = None
      for row in cursor: doc = Document(row)
      return doc


  def img(self, page):
      """
      Get the name of the image associated with the 
      document and page. 
      
      page : int
         The page to get.
      """
      return "%d%04d"%(self._get_row("id"), page)


  def get_page_text(self, pagenum):
      """
      Get the text of a page of the document.

      pagenum :
         The page to get. 
      """
      words = self._get_row("body").replace("<", " <").split()
      count = 0
      out = []
      for w in words:
          if w == "<?PRE?>": count +=1 
          if count == pagenum: out.append(w)
          if count > pagenum: break
      return " ".join(out)


  # def get_page(self, start):
  #     """
  #     Converts a word index into a page.
  #     """
  #     words = self.text.split()
  #     s = sum([1 for w in words[:start] if w == "<?PRE?>"])
  #     return s


#   "Representation of a DDRS document."
#   def get_words(self, start, stop):
#     "Get the words between start and stop range."
#     words = self.text.split()
#     return words[start:stop]

#   def get_page_text(self, pagenum):
#     "Get the text of a page of the document."
#     words = self._get_row("body").replace("<", " <").split()
#     count = 0
#     out = []
#     for w in words:
#       if w == "<?PRE?>": count +=1 
#       if count == pagenum: out.append(w)
#       if count > pagenum: break
#     return " ".join(out)

#   def get_page(self, start):
#     "Converts a word index into a page."
#     words = self.text.split()
#     s = sum([1 for w in words[:start] if w == "<?PRE?>"])
#     return s

#   @staticmethod
#   def columns():
#     "The names of the columns needed."
#     return ("written", "published", "classification", "sanitation", "completeness", 
#             "keyword", "pages", "title", "id", "body", "ficheid")


#   @staticmethod
#   def fetch_all(c):
#     "Get a document by its id."
#     q = "select * from Document "
#     c.execute(q)
#     for row in c: yield Document(row)
    

  
#   def processed_year(self):
#     "DDRS processing year."
#     return self._get_row("ficheid")[:4]


# def rejoin_page_text(text):
#   c = re.compile(r"\\n\\n|<\?BR\?>|<PARA>")
#   l1 = re.split(c, text.replace("</PARA>", "<PARA>"))
#   return "\n".join([l.strip() for l in l1]).strip()
