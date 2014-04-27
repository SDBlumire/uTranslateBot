import goslate
import unidecode
import praw
import time
import sys

#Set Up
gs = goslate.Goslate()                              #Translator Varaible
lang = gs.get_languages()                           #Laguages Index
langi = {v:k for k, v in lang.items()}              #Language Code Index
reddit = praw.Reddit(user_agent='uLinguaBot')       #Set up Reddit User Agent
passw = raw_input('Input LinguaBot Password: ')     #Get Bots Password
reddit.login('LinguaBot', passw)                    #Log into LinguaBot
#reddit.login('LinguaBot', sys.argv[1])

#Get Strings (Function taken from internet)
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

#main loop
while True:

    #Record epoch time the loop started
    tstart = time.time()

    #Check unread messages
    for msg in reddit.get_unread(limit=None):
        
        #Get the contents of the message
        msgs = msg.body
          
        #Split the message into it's arguments
        msga = msgs.split()
        
        #If the send information is a command
        if msga[0].lower() == '+/u/linguabot':
            
            #Clear the TSF variable so that we do not repeat ourselves
            tsf = []

            #Find the string that the user wants converted
            ts = find_between(msgs, '"', '"')

            #If no translation string is provided and the comment is not top level
            if ts == "" and msg.is_root == False:
                ts = reddit.get_info(thing_id=msg.parent_id).body
                

            #Find the languages the user wants to translate to
            langs = find_between(msgs, "[", "]").split()

            #Detect if the user has specified a language
            lf = find_between(msgs, "(", ")").title()

            #If the user has not specified a language autodetect it.
            if lf == "":
                lf = lang[gs.detect(ts)]
                
            #Inform the user which translated language was specified or detected
            tsf.append("Translating from " + lf + "\n\n___\n\n")
            
            #For each language they want translated
            for x in langs:
                
                #Capitalize the first letter of the language to format it properly
                x = x.title()
                
                #If that language is valid
                if x in langi and lf in langi:
                    
                    #Translate their string into that language
                    a = gs.translate(ts, langi[x], langi[lf])                     

                    #Transliterate the foreign alphabet into english
                    b = unidecode.unidecode(a)

                    #If the transliteration and the original are not the same
                    if a != unicode(b):

                        #Add the transliteration after the original
                        a = a + " / " + unicode(b)

                    #And add the translation to our translations list
                    tsf.append(a)

                #If the language is not valid
                else:

                    #Add the fact this cannot be used to the list
                    tsf.append(x + " is not a supported language")

            #If a translation has been done
            if tsf != []:

                #Give the user each of their translations, separated by lines.
                msg.reply("\n\n".join(tsf))
                
        #Mark the message read so it's not processed twice
        msg.mark_as_read()

    #Wait 15 seconds after finishing one pass to go again, so that the bot isn't working non stop.
    time.sleep(15)
