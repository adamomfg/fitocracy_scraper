#!/bin/python

"""
Scrapes fitocracy and creates a text file with the date, lift, set, reps and weight for each lift

Sample output:
    Sep 17, 2011:Barbell Squat:3:5:185

Requires:
    spynner (pip install spynner) (uses qt4)
    beautifulsoup4 (pip install beautifulsoup4)
    python2

---

Copyright 2012 Ben Backes

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
---

"""

"""
FILL IN YOUR FITOCRACY LOGIN DETAILS BELOW -- IMPORTANT
make sure you use quotes. ex:
    username = 'silverhydra'
    password = 'bcaacheatmodedyel'
"""
#ENTER INFO HERE!
username = ''
password = ''

#FILL IN THE PATH TO SAVE THE TEXT FILE
#ex: '/home/freddy/fitocracy.txt'
outputfile = ''


"""if desired, change character between entries
    date : lift : set : reps : weight
    don't use commas since they are in some lift names"""
seperator = ':'


#get comments too?
get_comments = 1



#CODE BEGINS HERE
from bs4 import BeautifulSoup
import sys
import re
import time
from time import sleep

import spynner
import pyquery





def getHtml():
    websiteProfile = 'http://www.fitocracy.com/profile/'
    websiteLogin = 'http://www.fitocracy.com/accounts/login/'

    br = spynner.browser.Browser()
    br.load(websiteProfile)
    br.create_webview()
    #br.show()

    br.wk_fill('input[id=id_username]', username)
    br.wk_fill('input[id=id_password]', password)
    br.click_ajax("#login_button")
    print "Logging in..."
    sleep(5)

    print br._get_url()
    
    for i in range(0,20):
        br.wk_click_ajax('#load_more_from_stream')
        print "clicking next..."
        sleep(1)
    
    myhtml = br._get_html()

    #for testing so i dont have to scrape every time
    """
    f = open('/home/ben/fitocracy.html', 'w')
    f.write(myhtml)
    f.close()
    """
    br.close()
    return myhtml
    

def main():
    txtfile = open(outputfile, 'w')
    
    f = getHtml()

    #just for testing
    #f = open('/home/ben/fitocracy.html', 'r')

    soup = BeautifulSoup(f)
    actions = soup.find_all("div", "action")
    for action in actions:
        try:
            atags = action.find_all('a')
            date = atags[1].contents[0] #date
        except:
            pass

        #get comments
        litags = action.find_all('li', 'user_comment clearfix')
        users = ''
        comments = []
        for tag in litags:
            for p in tag.find_all('p'):
                try:
                    comments.append(str(p.contents[2]))
                    for span in p.find('span'):
                        user = str(span.string)
                        users = users + ',' + user

                except:
                    pass
        
        #clean up comments 
        newusers = []
        newcomments = []
        for user in users.split(','):
            if user == '\n':
                continue
            elif user == '':
                continue
            else:
                newusers.append(user.strip())
        
        for comment in comments:
            if comment == '\n':
                continue
            elif comment == '':
                continue
            else:
                newcomments.append(comment.strip())
        

        span = action.find_all('span')
        for tag in span:
            try:
                if tag.has_key('style'): #style is used for hidden elements
                    continue 
                if tag.find(text = " weighted"):  #messes up formatting
                    continue 
                if date == tag.contents[0]: #don't need to print date again
                    continue
                if not tag.find(text = re.compile('\d')):
                    lift = tag.contents[0]
                    lift = re.search(r'(.+)(:)', lift).group(1)
                    weight = '0 lb'
                    set = 1
                    continue
                if tag.find(text = re.compile('lb')) or tag.find(text = re.compile('kg')):
                    weight = tag.contents[0]
                    continue

                if tag.find(text = re.compile('reps')):
                    reps = tag.contents[0]

                    #look for user comments
                    note = ''
                    next_note = tag.find_next("li", "stream_note")
                    if next_note.parent == tag.parent.parent:
                        note = next_note.contents[0]

                    #make output look nice
                    reps = re.search(r'(\d+)', reps).group()
                    weight = re.search(r'(\d+)', weight).group()
                    #date = time.strptime(date, "%b %d, %Y")
                    
                    output =  date + seperator + lift + seperator + str(set) + seperator + str(reps) + seperator + str(weight) +'\n'
                    if set == 1 and note and get_comments:
                        txtfile.write('\n' + note + '\n')
                    txtfile.write(output)
                    set = set + 1
               
            except:
                pass
        if get_comments:
            try:
                for i in range(len(newusers)):
                    output = newusers[i] + seperator +  newcomments[i] + '\n' + '\n'
                    txtfile.write(output)
            except:
                pass


    print "Writing file..."
    txtfile.close()
    #f.close()



if __name__ == '__main__':
    main()

