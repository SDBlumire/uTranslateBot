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
#passw = raw_input('Input LinguaBot Password: ')     #Get Bots Password
#reddit.login('LinguaBot', passw)                    #Log into LinguaBot
reddit.login('LinguaBot', sys.argv[1])

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

        highflag = 0
        
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
                
                #Set the translation string to the body of the comment the user replied too
                ts = reddit.get_info(thing_id=msg.parent_id).body

            #If no translation string is provided and the comment is top level
            if ts == "" and msg.is_root == True:

                #Set the translation string to the self text of the post the user replied too
                ts = reddit.get_info(thing_id=msg.parent_id).selftext

            #Find the languages the user wants to translate to
            langs = find_between(msgs, "[", "]").split()

            #If the string says "All" supply all available for translation strings
            if langs[0].title() == "All":
                langs = "Gujarati Chinese Irish Galician Latin Lao Turkish Latvian Lithuanian Thai Telugu Tamil Yiddish Cebuano Yoruba German Danish Greek Esperanto Basque Zulu Spanish Russian Romanian Belarusian Bulgarian Malay Bengali Javanese Bosnian Japanese Catalan Welsh Czech Portuguese Filipino Punjabi Polish Armenian Croatian Hungarian Hmong Hindi Hausa Mongolian Maori Macedonian Urdu Maltese Ukrainian Marathi Afrikaans Vietnamese Icelandic Italian Hebrew Kannada Arabic Estonian Azerbaijani Indonesian Igbo Dutch Norwegian Nepali French Persian Finnish Georgian Serbian Albanian Korean Swedish Khmer Slovak Somali Slovenian Swahili English".split()

            #If the string says "Europe" or "European" supply all languages from Europe
            if langs[0].title() == "Europe" or langs[0].title() == "European" or langs[0].upper() == "EU":
                langs = "English Welsh Icelandic Norwegian Swedish Finnish Russian Portuguese French German Dutch Danish Polish Czech Polish Lithuanian Latvian Estonian Belarusian Ukrainian Romanian Hungarian Slovak Itallian Serbian Bulgarian Greek Turkish Irish Bosnian Croation Macedonian Albanian Slovenian Catalan Basque Galician Maltese Latin".split()


            #If the string says "EUW" give all western european languages
            if langs[0].upper() == "EUW":
                langs = "Irish English Welsh Icelandic Norwegian Swedish Danish German Dutch French Basque Spanish Catalan Galician Portuguese Maltese".split()

            #If the string says "EUE" give all eastern european languages
            if langs[0].upper() == "EUE":
                langs = list(set("English Welsh Icelandic Norwegian Swedish Finnish Russian Portuguese French German Dutch Danish Polish Czech Polish Lithuanian Latvian Estonian Belarusian Ukrainian Romanian Hungarian Slovak Itallian Serbian Bulgarian Greek Turkish Irish Bosnian Croation Macedonian Albanian Slovenian Catalan Basque Galician Maltese Latin".split()) - set("Irish English Welsh Icelandic Norwegian Swedish Danish German Dutch French Basque Spanish Catalan Galician Portuguese Maltese".split()))

            #If the strong says "Scandinavian" or "EUSC" give all scandinavian languages
            if langs[0].title() == "Scandinavian" or langs[0].upper() == "EUSC":
                langs = "Danish Nowegian Swedish Icelandic".split()
            
            #Detect if the user has specified a language
            lf = find_between(msgs, "(", ")").title()

            #If the user has not specified a language autodetect it.
            if lf == "":
                lf = lang[gs.detect(ts)]

            #If the user is abusing the bot set the high flag
            if len(langs) > 85:
                highflag = 1

            #Inform the user which translated language was specified or detected
            tsf.append("#Translating from " + lf + "\n\n___\n\n")

            #If the user is not abusing the bot
            if highflag == 0:
                
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
                            a = a + "\n\n___\n\n **Transliterated " + x + "** \n\n" + unicode(b)

                        #add an underline after the translation
                        a = a + "\n\n___\n\n"

                        #add a title before the translation
                        a = "**" + x + "**\n\n" + a
                                                               
                        #And add the translation to our translations list
                        tsf.append(a)

                    #If the language is not valid
                    else:

                        #Add the fact this cannot be used to the list
                        tsf.append("**" + x + "**\n\n" + " is not a supported language \n\n___\n\n")

                      
                #If a translation has been done
                if tsf != []:

                    #Give the user each of their translations, separated by lines.
                    try:
                        msg.reply("\n\n".join(tsf))
                    except praw.errors.RateLimitExceeded as error:
                        time.sleep(error.sleep_time)
		    except praw.errors.APIException as error:
			try:
				msg.reply("Returned Translations are too long for a single comment. Please translate less in one go!")
			except praw.errors.RateLimitExceeded as error:
				time.sleep(error.sleep_time)
		    except:
			try:
				msg.reply("Unexpected Error. You probably tied to translate too much at once")
			except praw.errors.RateLimitExceeded as error:
				time.sleep(error.sleep_time)


            #If the user is abusing the bot
            elif highflag == 1:

		#Tell them to stop
                try:
                    msg.reply("The bot has detect an attempt at abuse. Please don't do this again.")
                except praw.errors.RateLimitExceeded as error:
                        time.sleep(error.sleep_time)
                        
        #Mark the message read so it's not processed twice
        msg.mark_as_read()
