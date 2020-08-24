from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from bs4 import BeautifulSoup
from urllib.request import urlopen
from .forms import InputForm
import time
import math

# import unicodedata

# songInfo = [[]]  # mostly used in learning how to scrape
lyrics = [[[], str]]  # stores [ [ [ lyrics to a song ], song information ] ], use this for similarity calculations
links = set()  # creates a set which holds links for processing
search = str
similarityArray = []


# Create your views here.


def get_website_info(response):
    # unicodedata.normalize('NFKD', response).encode('ascii', 'ignore')  # attempt at fixing unicode errors
    bs_obj = BeautifulSoup(response, "html.parser")
    if bs_obj:
        pages = bs_obj.find_all("a", {"class": ["song-link hasvidtoplyric", "title hasvidtoplyriclist"]})
        # {"class": ["song-link hasvidtoplyric", "title hasvidtoplyriclist"]}
        # as class arg above to go through all 100 songs instead of 20 ^
        # {"class": "song-link hasvidtoplyric"} as class arg for 20 songs
        # useful in shortening testing time and to spam their servers less

        if pages:
            for page in pages:
                links.add(page["href"])
            if links:
                i = 0
                for next_page in links:
                    i += 1
                    # time.sleep(2)  # as to not spam their servers, change how you see fit
                    page_response = urlopen(url=next_page)
                    bs_obj = BeautifulSoup(page_response, "html.parser")
                    lyric_content = get_lyric_content(bs_obj)
                    if lyric_content is not []:
                        # print(i, end=' ')
                        # print(next_page)
                        # print(lyric_content)
                        song_info = get_info(bs_obj)
                        # print(song_info)
                        lyrics.append([lyric_content, song_info])
                    print("\nScraping the song webpages. Give it some time...")
                print("\nDone scraping song webpages.\n")


def get_lyric_content(bs_obj):  # returns the lyrics to a song
    all_lyrics = bs_obj.find_all("p", {"class": "verse"})
    lyric_content = []

    for element in all_lyrics:
        lyric_content.append(element.get_text())

    # lyrics = []
    # # lyric = ''
    # if all_lyrics:
    #     print(all_lyrics)
    #     for tag in all_lyrics:
    #         if hasattr(all_lyrics, 'text'):
    #             print(tag)
    #             lyric = tag.get_text()
    #             print(lyric)
    #             lyrics.append(lyric)
    #     # print(lyric)

    return lyric_content


def get_info(bs_obj):  # returns information about song
    song_info = bs_obj.find_all("div", {"class": "banner-heading"})
    song = str
    for element in song_info:
        song = (element.find("h1").get_text())
    return song


# def get_song_info(bs_obj):  # OBSOLETE: returned information about a song
#     # i = 0
#     song_info1 = bs_obj.find_all("span", {"class": "song"})
#     if song_info1:
#         for tag in song_info1:
#             # i += 1
#             if hasattr(song_info1, 'text'):
#                 artist_name = tag.find("a", {"class": "subtitle"}).text
#                 song_title = tag.find("a", {"class": "song-link hasvidtoplyric"}).text
#                 songInfo.append([artist_name, song_title])
#                 # print(i)
#                 # print(artist_name, song_title)
#
#     song_info2 = bs_obj.find_all("li", {"class": "hasvid"})
#     if song_info2:
#         for tag in song_info2:
#             if hasattr(song_info2, 'text'):
#                 # i += 1
#                 artist_name = tag.find("a", {"class": "subtitle"}).text
#                 # artistArray.append(artist_name)
#                 song_title = tag.find("a", {"class": "title hasvidtoplyriclist"}).text
#                 # songArray.append(song_title)
#                 songInfo.append([artist_name, song_title])
#                 # print(i)
#                 # print(artist_name, song_title)


def calculateSimilarity(searchQuery):
    #print("\n\n")
    #print(searchQuery)
    #print("\n\n")
    searchTerms = searchQuery.lower().split()
    searchFreqList = {}
    similarityArray = []
    newSimArray = []
    # turn search terms into frequency list
    for term in searchTerms:
        if term in searchFreqList:
            searchFreqList[term] += 1
        else:
            searchFreqList[term] = 1

    for song in lyrics:
        freqList = {}
        # turn song into frequency list
        doclen = 0
        for line in song[0]:
            for word in line.split():
                doclen += 1
                if word in freqList:
                    freqList[word] += 1
                else:
                    freqList[word] = 1
        print("The number of lyrics is ", doclen)
        if doclen == 0:
            continue
        #print("doclen is ", doclen)

        # make sure all terms have a value
        print("number of words in freqlist: ", len(freqList))
        print("number of words in searchFreqList: ", len(searchFreqList))
        for key in freqList:
            if key not in searchFreqList:
                searchFreqList[key] = 0
        for key in searchFreqList:
            if key not in freqList:
                freqList[key] = 0

        # calculate similarity
        # similarity = (A dot B) / (||A|| * ||B||), where ||A|| is the length of A
        numerator = 0
        denominator = 0
        for word in searchFreqList:
            if word in freqList:
                numerator += freqList[word] * searchFreqList[word]
            denominator = len(searchTerms) * doclen
        similarityArray.append((song[1], (numerator / denominator)))
        print("Similarity vector length is ", len(similarityArray))

        def getSecond(term):
            return term[1]
    # sort and reverse the similarity vector to get the rankings in order from most similar to least similar

    newSimArray = sorted(similarityArray, key=getSecond, reverse=True)
    return newSimArray


def index(request):
    res = urlopen("https://www.metrolyrics.com/top100.html")
    get_website_info(res)

    template = loader.get_template('SongFound/index.html')

    #print("\n\n")
    #print(lyrics)
    #print("\n\n")
    # print(lyrics[3][1])

    form = InputForm()
    return render(request, 'SongFound/index.html', {'form': form})


def results(request):
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            search = str(form.data['search'])

    form = InputForm()
    similarityArray.clear()
    ranking = calculateSimilarity(search)

    # print("RESULTS ARE:")
    # for element in ranking:
    #     print (element, "\n")

    return render(request, "SongFound/results.html", {
        'form': form,
        'search': search,
        'ranking': ranking,
    })
