
# In[1]:

import sys
sys.path.insert(0, "/home/srush/Projects/declass-align/")


# In[52]:

import redact.baselines as baselines
import redact.experiments
import matplotlib.pyplot as plt
import cv2
import numpy as np
import redact.images as im


# In[3]:

from redact.data.human import * 
import redact.data.passwd as passwd
db = passwd.get_db()
cursor = passwd.get_cursor(db)
all = HumanPair.get_all(cursor)


# In[175]:

p1, p2 = baselines.make_docs(all[10])


# In[178]:

ta = baselines.TextAligner()
for prediction in ta.align(p1, p2, 0):
    print prediction


# Out[178]:

#     0 1 4->12  THEM IN DUE COURSE. PANAMA HAD NOW TAKEN POSITION
#     0 1 18->19  AND ALMOST PITIFUL PLEAS THAT COMMISSION CONTINUE
# 

# In[184]:

imshow(im.make_side_by_side(p1.z, p2.z))


# Out[184]:

#     <matplotlib.image.AxesImage at 0x21197e50>

# image file:

# Step 1. Warp the second image to line up with the first. Afterwards they should mostly overlap.

# In[179]:

figure(figsize = (10,5))
warp = im.align_images(p1.z, p2.z)
imshow(cv2.absdiff(p1.z, warp))


# Out[179]:

#     <matplotlib.image.AxesImage at 0x20a65b10>

# image file:

# Step 2. Clean and deskew the images.

# In[180]:

figure(figsize = (10,5))
im1 = im.clean_text_image(p1.z)
im2 = im.clean_text_image(warp)
imshow(cv2.absdiff(im1, im2))


# Out[180]:

#     <matplotlib.image.AxesImage at 0x211eecd0>

# image file:

# Step 3. Convert the images to lines.

# In[188]:

boxes1 = im.find_lines(im1)
boxes2 = im.find_lines(im2)


# We can draw the boxes back on to the images like this. 

# In[189]:

figure(figsize = (10,5))
tmp_im1 = np.array(im1)
tmp_im2 = np.array(im2)
for box in boxes1: im.draw_box(tmp_im1, box)
for box in boxes2: im.draw_box(tmp_im2, box)
imshow(tmp_im1)


# Out[189]:

#     <matplotlib.image.AxesImage at 0x23eca490>

# image file:

# In[183]:

figure(figsize = (10,5))
imshow(tmp_im2)


# Out[183]:

#     <matplotlib.image.AxesImage at 0x2116e050>

# image file:

# Now we might want to compare the two sets of boxes. 

# In[127]:

import difflib as dl
import redact.image_utils as im_util
from redact.text_utils import *


# In[191]:

ims = [np.array(im1), np.array(im2)]
boxes = [boxes1, boxes2]
for op in im_util.fuzzy_box_align(boxes1, boxes2):
    if op[0] != "equal":
        r = Range.from_op(op)
        side = 0 if r[0].num_lines() > r[1].num_lines() else 1
        print r[side]
        for box in boxes[side][r[side].start.line:r[side].end.line]: 
            im.draw_box(ims[side], box)
figure(figsize = (10,5))
imshow(ims[0])


# Out[191]:

#     0->2
#     9->16
# 

#     <matplotlib.image.AxesImage at 0x245f1e10>

# image file:

# In[192]:

figure(figsize = (10,5))
imshow(ims[1])


# Out[192]:

#     <matplotlib.image.AxesImage at 0x2461d9d0>

# image file:

# In[40]:

match = im.draw_matches(p1.z, p2.z, pairs, key1, key2)
imshow(match)


# Out[40]:

#     <matplotlib.image.AxesImage at 0x65e6810>

# image file:

# In[48]:

imshow(im.warped_image_to_match(p1.z, p2.z, points1, points2))


# Out[48]:

#     <matplotlib.image.AxesImage at 0x8e82cd0>

# image file:

# In[42]:

print p1


# Out[42]:

#     0: B
#     1:  from the Netherlands, and head of the Army Strategie 
#     2:  Command. is reputation within Indonesia as a highly 
#     3:  competent officer nd an anti-Communist was amply 
#     4:  verified by his prompt and decisive action on 1 October 
#     5:  to rally the army and crush the coup.  
#     6: 14. General Nasution was commander of the army 
#     7:  from 1949 to 1952 and again from 1955 to 1962. He is 
#     8:  largely responsible for the professionalism and cohesiveness 
#     9:  which the army has thus far achieved. From 
#     10:  1952-55 Nasution was in retirement as the result of 
#     11:  opposition to a nationalist-Communist parliamentary 
#     12:  coalition and indirectly to Sukarno. From 1957 to 
#     13:  1960, when the army held a strong political position, 
#     14:  Nasution was easily the second most powerful official 
#     15:  in the country. In 1962, apparently to deprive him 
#     16:  of troop command, Sukarno appointed him chief of staff 
#     17:  of the armed forces.  
#     18: In the post-sukarno era, Nasution probably 
#     19:  would be the army\'s major candidate for national leadership.  
#     20: 15. Fifteen army officers, including Suharto 
#     21:  and Nasution, hold posts in the 100-man cabinet. One 
#     22:  who is currently active in his cabinet capacity and 
#     23:  likely to continue in this role regardless of future 
#     24:  developements is General Ibnu Sutowo, minister if sitate 
#     25:  for gas and oil since last march. Sutowo had one tour 
#     26:  as a territorial commander in South Sumatra in the 
#     27:  mdi-50s, and served in Djakarta as army deputy for 
#     28:  administration, deputy gfor territorial affairs, and 
#     29:  chief of logistics during Nasution\'s second tour as 
#     30:  army commander.  
#     31: Since then he has 
#     32:  ween continuously active in oil matters and since 1961 
#     33:  his responsibilities have gradually increased.  
#     34: T
#     35: T
# 

# In[43]:

print p2


# Out[43]:

#     0: B
#     1:  from the Netherlands, and head of the Army Strategic 
#     2:  Command. His reputation within Indonesia as a highly 
#     3:  competent officer and an anti-Communist was amply 
#     4:  verified by his prompt and decisive action on 1 October 
#     5:  to rally the army and crush the coup. He is also reputed 
#     6:  to be strong willed and dogmatic, qualities 
#     7:  which for the time being appear to assist the army in 
#     8:  its continuing resistance to Sukarno. 
#     9:  14. General Nasution was commander of the army 
#     10:  from 1949 to 1952 and again from 1955 to 1962. He is 
#     11:  largely responsible for the professionalism and cohesiveness 
#     12:  which the army has thus far achieved. From 
#     13:  1952-55 Nasution was in retirement as the result of 
#     14:  opposition to a nationalist-Communist parliamentary 
#     15:  coalition and indirectly to Sukarno. From 1957 to 
#     16:  1960, when the army held a strong political position, 
#     17:  Nasution was easily the second most powerful official 
#     18:  in the country. In 1962, apparently to deprive him 
#     19:  of troop command, Sukarno appointed him chief of staff 
#     20:  of the armed forces 
#     21:  In the post-Sukarno ear, Nasution probably 
#     22:  would be the army\'s major candidate for national leadership. 
#     23:  15. Fifteen army officers, including Suharto 
#     24:  and Nasution, hold posts in the 100-man cabinet. One 
#     25:  who is currently active in his cabinet capacity and 
#     26:  likely to continue in this role regardless of future 
#     27:  developments is General Ibnn Sutowo, minister of state 
#     28:  for gas and oil since last March. Sutowo had one tour 
#     29:  as a territorial commander in South Sumatra in the 
#     30:  mid-50s, and served in Djakarta as army deputy for 
#     31:  administration, deputy for territorial affairs, and 
#     32:  chief of logistics during Nasution\'s second tour as 
#     33:  army commander. 
#     34:  Since then he has 
#     35:  been continuously active in oil matters and since 1961 
#     36:  his responsibilities have gradually increased. For 
#     37:  several years he has been involved in political maneuvering 
#     38:  against Chaerul Saleh, who holds the actual 
#     39: T
#     40: T
# 

# In[50]:

reload(baselines)
ta = baselines.TextAligner()
for prediction in ta.align(p1, p2, 0):
    print prediction


# Out[50]:

#     0 1 6->9  to be strong willed and dogmatic, qualities 
#      whi
#     0 1 37->39  several years he has been involved in political m
# 
