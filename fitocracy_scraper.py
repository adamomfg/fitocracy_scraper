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
get_comments = 0


from bs4 import BeautifulSoup
import sys
import re
import time
from time import sleep

import spynner
import pyquery

testing_output = 0
debug = 0

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

    if testing_output:
        f = open('/home/ben/fitocracy.html', 'w')
        f.write(myhtml)
        f.close()

    br.close()
    return myhtml

def cleanOutput(date, lift, set, reps, weight):
    reps = re.search(r'(\d+)', reps).group()
    weight = re.search(r'(\d+)', weight).group()
    
    output =  date + seperator + lift + seperator + str(set) + seperator + str(reps) + seperator + str(weight) +'\n'
    return output

def getComments(action):
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
    return newusers, newcomments 



def main():
    txtfile = open(outputfile, 'w')
    if testing_output:
        f = open('/home/ben/fitocracy.html', 'r')
    else:
        f = getHtml()

    soup = BeautifulSoup(f)
    actions = soup.find_all("div", "action")

    #all the actions
    for action in actions:

        try:
            atags = action.find_all('a')
            date = atags[1].contents[0] 
        except:
            pass

        #get comments
        if get_comments:
            newusers, newcomments = getComments(action)

        unwritten_chin = 0

        span = action.find_all('span')
        for tag in span:
            try:
                if tag.has_key('style'): #style is used for hidden elements
                    if debug:
                        print 'found a hidden element. skipping...'
                    continue 
                if tag.find(text = " weighted"):  #messes up formatting
                    if debug:
                        print 'found weighted in name. skipping...'
                    continue 
                if date == tag.contents[0]: 
                    continue

                #lift name
                if not tag.find(text = re.compile('\d')):
                    if unwritten_chin:
                        output = cleanOutput(date, lift, set, reps, weight)
                        if set == 1 and  get_comments:
                            if note:
                                txtfile.write('\n' + note + '\n')
                        txtfile.write(output)
                        set = set + 1
                        unwritten_chin = 0


                    lift = tag.contents[0]
                    lift = re.search(r'(.+)(:)', lift).group(1)
                    weight = '0 lb'
                    set = 1
                    if debug:
                        print 'found the lift name: ', lift
                    continue

                #lbs
                if tag.find(text = re.compile('lb')) or tag.find(text = re.compile('kg')):

                    weight = tag.contents[0]
                    if debug:
                        print 'found the weight: ', weight
                    if re.search(r'Dips', lift) or re.search(r'Pull-Up', lift) or re.search(r'Chin-Up', lift):
                        output = cleanOutput(date, lift, set, reps, weight)
                        if debug:
                            print 'looks like a dip or pull up. writing output... \n', output
                        txtfile.write(output)
                        unwritten_chin = 0
                        set = set + 1
                        if set == 1 and note and get_comments:
                            txtfile.write('\n' + note + '\n')
                    continue

                #reps
                if tag.find(text = re.compile('reps')):
                    if unwritten_chin:
                        output = cleanOutput(date, lift, set, reps, weight)
                        if set == 1 and  get_comments:
                            if note:
                                txtfile.write('\n' + note + '\n')
                        txtfile.write(output)
                        set = set + 1
                        unwritten_chin = 0

                    reps = tag.contents[0]
                    if debug:
                        print 'found the reps ', reps

                    if get_comments:
                        note = ''
                        next_note = tag.find_next("li", "stream_note")
                        if next_note.parent == tag.parent.parent:
                            note = next_note.contents[0]

                    if not (re.search(r'Dips', lift) or re.search(r'Pull-Up', lift) or re.search(r'Chin-Up', lift)):
                        output = cleanOutput(date, lift, set, reps, weight)
                        if debug:
                            print 'looks like normal weights. writing outout\n ', output
                        if set == 1 and  get_comments:
                            if note:
                                txtfile.write('\n' + note + '\n')
                        txtfile.write(output)
                        set = set + 1
                    else:
                        unwritten_chin = 1
              
            except:
                pass

        if get_comments:
            try:
                for i in range(len(newusers)):
                    output = newusers[i] + seperator +  newcomments[i] + '\n' + '\n'
                    txtfile.write(output)
            except:
                pass


    print "Writing file to" + ' ' + outputfile
    txtfile.close()
    if testing_output:
        f.close()




if __name__ == '__main__':
    main()

