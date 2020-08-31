from bs4 import BeautifulSoup
import requests
import pypub
import os
import json

with open("serialinfo.json") as json_file:
    json_format = json.load(json_file)
    
with open("webseriallist.json") as json_file:
    json_info = json.load(json_file)

# Loop through the web serials in webseriallist.json
for serials in json_info["webserials"]:
    title      = serials["serialtitle"]
    author     = serials["serialauthor"]
    chapterurl = serials["serialurl"]
    
    my_epub = pypub.Epub(title + ' by ' + author)
    print('Downloading ' + title + ' by ' + author)

    # Loop through the chapters in a web serial
    while True:
    
        # Check if chapter is excluded
        exclude = False;
        
        with open("exclusionlist.txt", "r") as exclusionlist:
            while True: 
                line = exclusionlist.readline()
                if not line:
                    break
                if chapterurl == line.strip():
                    exclude = True
                    break
                if "prefix" in serials:
                    if serials["prefix"] + chapterurl == line.strip():
                        exclude = True
                        break
            
        try:
            chapter = requests.get(chapterurl)
        except requests.exceptions.MissingSchema:
            chapter = requests.get(serials["prefix"] + chapterurl)
        
        soup = BeautifulSoup(chapter.text, "html.parser")

        results = soup.find("body")
        
        # Find the chapter title and text
        if exclude is False:
            chapterTitle = "title"
            chapterText = "text"
            
            for title in json_format["title"]:
                if results.find(title["element"], class_= title["class"]) is not None:
                    chapterTitle = results.find(title["element"], class_= title["class"])
                    break
                    
            for content in json_format["content"]:
                if results.find('div', class_=content) is not None:
                    chapterText = results.find('div', class_=content)
                    break
                
            finalChapterText = "text"
            chapterTitle = chapterTitle.text.strip()
            chapterTitle = chapterTitle.replace('  ', ' ')
            print(chapterTitle)

            for paragraphs in chapterText:
                if paragraphs.find('a') is None:
                    finalChapterText = str(paragraphs)

            my_chapter = pypub.create_chapter_from_string(finalChapterText, url=None, title=chapterTitle)
            my_epub.add_chapter(my_chapter)
                
        
        # Find the link to the next chapter
        foundNextChapter = False        
        for a in soup.find_all('a', href=True):
            tag = a.text
            tag = tag.replace(u'\xa0', '')
            tag = tag.replace(' ', '')
            for listitem in json_format["nextchapter"]:
                if tag.startswith(listitem):
                    if chapterurl == a['href'].strip():
                        chapterurl = input("The listed next page is the same as the current. Please enter the URL for the correct next page: ")
                    else:
                        chapterurl = a['href'].strip()
                    foundNextChapter = True;
                if foundNextChapter:
                    break;
            if foundNextChapter:
                break;
            
        if foundNextChapter is False:
            break;


    my_epub.create_epub(os.getcwd())