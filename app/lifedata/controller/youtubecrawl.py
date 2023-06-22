import xml.etree.ElementTree as ET
from datetime import datetime
from xml.dom import minidom
import urllib.request
import html2text
import json
import sys
import csv
import os
import re
import xmltodict
from pprint import pformat
from app.controller import (
    life_logging
)
from app.lifedata.controller import (
    save_crawled_data
)

logger = life_logging.get_logger()

key = ""

# List of channels : mention if you are pasting channel id or username - "id" or "forUsername"
# getVideoCount()

#ytids = [["bbcnews", "forUsername"], ["UCjq4pjKj9X4W9i7UnYShpVg", "id"]]
ytids = []
prev_videos = set()
csv_data = []
meta = []
video_count = 0
ccount = 0
crcount = 0
tccount = 0
data_links_info = {}


def getCommentData(datac, utube, chid, vid):
    global ccount
    global crcount
    global video_count
    global meta
    global csv_data
    global tccount

    for data in datac['items']:
        ccount += 1
        tccount += 1
        logger.debug('Video:\t %s, \tComment:\t %s', video_count, ccount)
        cid = data['id']
        topc = data['snippet']['topLevelComment']['snippet']
        org_text = topc['textOriginal']
        final_text = topc['textDisplay']
        org_dt = topc['publishedAt']
        org_date = org_dt[:org_dt.find('T')]
        org_time = org_dt[org_dt.find('T')+1:]
        final_dt = topc['updatedAt']
        final_date = final_dt[:final_dt.find('T')]
        final_time = final_dt[final_dt.find('T')+1:]
        author = topc['authorDisplayName']
        likes = topc['likeCount']
        rating = topc['viewerRating']
        replies = int(data['snippet']['totalReplyCount'])

        async_c = ET.SubElement(utube, 'async_comment', {'id': str(ccount)})

        cinfo = ET.SubElement(async_c, 'comment_info')
        ctr = ET.SubElement(cinfo, 'commentator')
        ctr.text = str(author)
        dat = ET.SubElement(cinfo, 'published_date')
        dat.text = str(org_date)
        tm = ET.SubElement(cinfo, 'published_time')
        tm.text = str(org_time)
        dat_f = ET.SubElement(cinfo, 'final_date')
        dat_f.text = str(final_date)
        tm_f = ET.SubElement(cinfo, 'final_time')
        tm_f.text = str(final_time)
        lks = ET.SubElement(cinfo, 'likes')
        lks.text = str(likes)
        rat = ET.SubElement(cinfo, 'rating')
        rat.text = str(rating)
        rep = ET.SubElement(cinfo, 'replies')
        rep.text = str(replies)
        wrds = ET.SubElement(cinfo, 'words')
        wrds.text = str(len(final_text.split()))

        cmnt = ET.SubElement(async_c, 'comment_content')
        sc = 'Roman'
        
        if re.search(r"[\u0900-\u097F]+", final_text):
            if re.search(r"[A-Za-z]+", final_text):
                sc = 'Roman and Devanagari'
            else:
                sc = 'Devanagari'
        elif re.search(r"[\u0980-\u09FF]+", final_text):
            if re.search(r"[A-Za-z]+", final_text):
                sc = 'Roman and Bangla'
            else:
                sc = 'Bangla'

        org = ET.SubElement(cmnt, 'original_script', {'name': sc})
        org.text = str(final_text)

        intl = ET.SubElement(async_c, 'comment_content_initial')
        intl.text = str(org_text)

        # storing data for CSV. More information may be added later, based on requirement
        csv_data.append(['C' + str(video_count) + '.' + str(ccount), html2text.html2text(final_text).strip()])

        # Metadata for this comment
        meta_comment = []
        meta_comment.append(vid)  # video ID
        meta_comment.append(chid)  # channel ID
        meta_comment.append(cid)  # comment ID
        meta_comment.append('youtube_corpus_'+str(video_count))  # file name
        meta_comment.append(vid)  # parent_ID
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        meta_comment.append(dt_string)  # current date time
        meta.append(meta_comment)

        # Getting replies (if available)
        if replies > 0 and 'replies' in data:
            replies_a = data['replies']['comments']
            crcount = 0
            logger.debug('Video:\t%s \tComment:\t%s \tReplies on comment:\t%s', video_count, ccount, cid)
            for comment in replies_a:
                crcount += 1
                tccount += 1
                logger.debug('Video:\t%s \tComment:\t%s \tReply:\t%s', video_count, ccount, crcount)
                rep = comment['snippet']
                org_text = rep['textOriginal']
                final_text = rep['textDisplay']
                org_dt = rep['publishedAt']
                org_date = org_dt[:org_dt.find('T')]
                org_time = org_dt[org_dt.find('T')+1:]
                final_dt = rep['updatedAt']
                final_date = final_dt[:final_dt.find('T')]
                final_time = final_dt[final_dt.find('T')+1:]
                author = rep['authorDisplayName']
                likes = rep['likeCount']
                rating = rep['viewerRating']
                rid = comment['id']

                async_c = ET.SubElement(utube, 'async_comment', {
                                        'id': str(ccount) + '.' + str(crcount)})

                cinfo = ET.SubElement(async_c, 'comment_info')
                ctr = ET.SubElement(cinfo, 'commentator')
                ctr.text = str(author)
                dat = ET.SubElement(cinfo, 'published_date')
                dat.text = str(org_date)
                tm = ET.SubElement(cinfo, 'published_time')
                tm.text = str(org_time)
                dat_f = ET.SubElement(cinfo, 'final_date')
                dat_f.text = str(final_date)
                tm_f = ET.SubElement(cinfo, 'final_time')
                tm_f.text = str(final_time)
                lks = ET.SubElement(cinfo, 'likes')
                lks.text = str(likes)
                rat = ET.SubElement(cinfo, 'rating')
                rat.text = str(rating)
                wrds = ET.SubElement(cinfo, 'words')
                wrds.text = str(len(final_text.split()))

                cmnt = ET.SubElement(async_c, 'comment_content')
                sc = 'Roman'
                if re.search(r"[\u0900-\u097F]+", final_text):
                    if re.search(r"[A-Za-z]+", final_text):
                        sc = 'Roman and Devanagari'
                    else:
                        sc = 'Devanagari'
                org = ET.SubElement(cmnt, 'original_script', {'name': sc})
                org.text = str(final_text)

                intl = ET.SubElement(async_c, 'comment_content_initial')
                intl.text = str(org_text)

                # storing data for CSV. More information may be added later, based on requirement
                csv_data.append(['C' + str(video_count) + '.' + str(ccount) +
                                 '.' + str(crcount), html2text.html2text(final_text).strip()])

                # Metadata for this reply
                meta_reply = []
                meta_reply.append(vid)  # video ID
                meta_reply.append(chid)  # channel ID
                meta_reply.append(rid)  # comment ID
                meta_reply.append('youtube_corpus_' +
                                  str(video_count))  # file name
                meta_reply.append(cid)  # parent_ID
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                meta_reply.append(dt_string)  # current date time
                meta.append(meta_reply)

    return utube

def getAllVideosData (projects_collection,
                        userprojects_collection,
                        sourcedetails_collection,
                        crawling_collection,
                        project_owner,
                        current_username,
                        active_project_name,
                        datad,
                        search_keywords):
    for data in datad['items']:
            nlink = data['contentDetails']['videoId']
            getVideoData(projects_collection,
                            userprojects_collection,
                            sourcedetails_collection,
                            crawling_collection,
                            project_owner,
                            current_username,
                            active_project_name,
                            nlink,
                            search_keywords)

def getVideoData(projects_collection,
                    userprojects_collection,
                    sourcedetails_collection,
                    crawling_collection,
                    project_owner,
                    current_username,
                    active_project_name,
                    vlink,
                    search_keywords):
    global ccount
    global crcount
    global video_count
    global meta
    global csv_data
    global tccount        

    if vlink not in prev_videos:
        csv_data.clear()
        meta.clear()

        # Getting Video Data
        #ntitle = data['snippet']['title']
        urlv = "https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id="+vlink+"&key="+key
        with urllib.request.urlopen(urlv) as url:
            datav = json.loads(url.read())
            # logger.debugdatav)
        try :
            for vdata in datav['items']:
                # Checking if the video has comments
                stats = vdata['statistics']
                cmntc = '0'
                if 'commentCount' in stats:
                    cmntc = stats['commentCount']
                logger.debug('Total comments on video: %s : %s', vlink, cmntc)
                # Proceeding further if there are comments on video
                if int(cmntc) > 0:
                    metadata = vdata['snippet']
                    dt = metadata['publishedAt']
                    date = dt[:dt.find('T')]
                    time = dt[dt.find('T')+1:]
                    channel = metadata['channelTitle']
                    channel_id = metadata['channelId']
                    title = metadata['title']
                    description = metadata['description']

                    views = stats['viewCount']
                    if 'likeCount' not in stats:
                        likes = 0
                    else:
                        likes = stats['likeCount']
                    if 'dislikeCount' not in stats:
                        dislikes = 0
                    else:    
                        dislikes = stats['dislikeCount']
                    
                    favs = '0'
                    if 'favouriteCount' in stats:
                        favs = stats['favouriteCount']

                    lang = 'NA'
                    if 'defaultAudioLanguage' in metadata:
                        lang = metadata['defaultAudioLanguage']

                    vLink = "https://www.youtube.com/watch?v="+vlink

                    # Increasing file count
                    video_count += 1

                    # Adding for CSV File
                    csv_data.append(['Youtube Corpus ' + str(video_count), vLink])

                    # Comment count
                    ccount = 0
                    tccount = 0
                    
                    # Adding Video Data to XML
                    co3h = ET.Element('co3h')
                    async_c = ET.SubElement(co3h, 'asynchronous')
                    utube = ET.SubElement(async_c, 'youtube_video', {
                                        'id': str(video_count)})

                    async_i = ET.SubElement(utube, 'async_info')
                    pub = ET.SubElement(async_i, 'publisher')
                    pub.text = str(channel)
                    ttl = ET.SubElement(async_i, 'video_title')
                    ttl.text = str(title)
                    desc = ET.SubElement(async_i, 'video_description')
                    desc.text = html2text.html2text (str(description)).strip()
                    dat = ET.SubElement(async_i, 'date')
                    dat.text = str(date)
                    tm = ET.SubElement(async_i, 'time')
                    tm.text = str(time)
                    vws = ET.SubElement(async_i, 'total_views')
                    vws.text = str(views)
                    lks = ET.SubElement(async_i, 'likes')
                    lks.text = str(likes)
                    dlks = ET.SubElement(async_i, 'dislikes')
                    dlks.text = str(dislikes)
                    fav = ET.SubElement(async_i, 'favourites')
                    fav.text = str(favs)
                    cc = ET.SubElement(async_i, 'total_comments')
                    cc.text = str(cmntc)
                    lng = ET.SubElement(async_i, 'audio_language')
                    lng.text = str(lang)

                    main = ET.SubElement(utube, 'main_content')
                    org = ET.SubElement(main, 'original_script', {'name': 'Roman'})
                    org.text = str(vLink)

                    # Metadata for this video
                    meta_video = []
                    meta_video.append(vlink)  # video ID
                    meta_video.append(channel_id)  # channel ID
                    meta_video.append('NA')  # comment ID
                    meta_video.append('youtube_corpus_' +
                                    str(video_count))  # file name
                    meta_video.append('NA')  # parent_ID
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    meta_video.append(dt_string)  # current date time
                    meta.append(meta_video)

                    # Comments on the video
                    urlc = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId="+vlink+"&key="+key
                    with urllib.request.urlopen(urlc) as url:
                        datac = json.loads(url.read())

                    # get comments from first page
                    logger.debug('Video:\t:%s \tPage:\t1', video_count)
                    utube = getCommentData(datac, utube, channel_id, vlink)

                    # checking for more pages
                    #totalResults = int(datac['pageInfo']['totalResults'])
                    totalResults = int(cmntc)
                    perPage = int(datac['pageInfo']['resultsPerPage'])
                    totalPages = int(totalResults / perPage)
                    logger.debug('Total: %s pages of comments in video: %s', (totalPages+1), vlink)
                    logger.debug('Per page: %s \tTotal Pages: %s \tTotal Results: %s', perPage, (totalPages+1), totalResults)

                    # Iterating through multiple pages of videos on the channel
                    if totalResults > perPage:
                        for i in range(totalPages):
                            if 'nextPageToken' in datac:
                                pToken = datac['nextPageToken']
                                #logger.debug(pToken)
                                urlc = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId=" + \
                                    vlink+"&key="+key+"&pageToken="+pToken
                                #logger.debug(urlc)
                                try:
                                    with urllib.request.urlopen(urlc) as url:
                                        datac = json.loads(url.read())
                                    
                                    # get data from next pages
                                    logger.debug('Video:\t%s \tPage:\t%s', video_count, (i+2))
                                    utube = getCommentData(
                                        datac, utube, channel_id, vlink)
                                except Exception as e:
                                    logger.exception("")
                                    logger.debug('Exception: %s', e)
                                    logger.debug('urlc: %s', urlc)
                                    logger.debug('Page: %s out of total: %s pages of comments', i, totalPages)
                                    logger.debug('Expected total comments: %s', totalResults)
                                    logger.debug('Expected complete: %s', ccount)
                                    logger.debug('The program will now exit without writing data from video: %s', video_count)
                                    quit(403)
                            else:
                                logger.debug('Video:\t%s \tPage:\t%s', video_count, (i+2))
                                logger.debug('Total Comments:\t%s', tccount)
                                logger.debug('No more next pages')
                                if tccount != cmntc:
                                    cc.text = str(tccount)
                                break



                    logger.debug('Crawling complete. Now writing data and metadata to file')
                    # XML to String
                    #complete = ET.tostring(co3h)
                    complete = minidom.parseString(ET.tostring(co3h)).toprettyxml(indent="   ")

                    # File Name
                    fname = 'youtube_corpus_'+str(video_count)

                    # Writing XML File
                    # with open('xml-data-youtube/' + fname + '.xml', 'w') as f_w:
                    #     f_w.write(complete)
                    # logger.debug('xml-data-youtube: %s', complete)

                    # with open('xml-data-youtube/' + fname + '.xml', 'r') as f_r:
                    #     doc = xmltodict.parse(f_r.read())
                    # xml_to_json = json.dumps(doc, indent=2, ensure_ascii=False)
                    # logger.debug('xml_to_json: %s', xml_to_json)

                    doc = xmltodict.parse(ET.tostring(co3h))
                    xml_to_json = json.dumps(doc, indent=2, ensure_ascii=False)
                    logger.debug('xml_to_json TYPE: %s', type(xml_to_json))
                    logger.debug('xml_to_json: %s', xml_to_json)
                    xml_to_json = json.loads(xml_to_json)
                    # logger.debug('xml_to_json: %s', pformat(xml_to_json))
                    # logger.debug('xml_to_json TYPE: %s', type(xml_to_json))
                    # logger.debug('co3h TYPE: %s', type(co3h))
                    # logger.debug('co3h: %s', co3h)

                    # Writing CSV File
                    # with open('csv-data-youtube/' + fname + '.csv', 'w') as f_w:
                    #     writer = csv.writer(f_w, delimiter='\t')
                    #     writer.writerows(csv_data)
                    logger.debug('csv-data-youtube: %s', csv_data)

                    # Writing metadata file
                    # with open('youTubeLinks.tsv', 'a') as f_w:
                    #     writer = csv.writer(f_w, delimiter='\t')
                    #     writer.writerows(meta)
                    logger.debug('youTubeLinks.tsv: %s', meta)
                    
                    save_crawled_data.save_youtube_crawled_data(projects_collection,
                                                                    userprojects_collection,
                                                                    sourcedetails_collection,
                                                                    crawling_collection,
                                                                    project_owner,
                                                                    current_username,
                                                                    active_project_name,
                                                                    xml_to_json,
                                                                    csv_data,
                                                                    meta,
                                                                    vlink,
                                                                    search_keywords)
        except Exception:
            # traceback.logger.debugexc()
            logger.exception("")
            with open('linksnotparse.txt', 'a') as notparse:
                notparse.write("https://www.youtube.com/watch?v="+vlink+"\n")

#Function for retrieving the API key
def getKey():
    global key
    if os.path.exists('key.txt'):
        with open('key.txt') as f:
            key = f.read().strip()
    else:
        logger.debug(
            'API Key not found. Please paste your API key in key.txt file. See README for getting the key')
        sys.exit()


# Function for retrieving the list of channels and videos from where data is to be collected
def getList():
    global ytids
    if os.path.exists('channels.txt'):
        with open('channels.txt') as f:
            for channel in f:
                ytids.append([channel.strip(), "id"])
    else:
        logger.debug(
            'List of channels not found. Please give the ID of channels in channels.txt file')
    
    if os.path.exists('videos.txt'):
        with open('videos.txt') as f:
            for video in f:
                video_id = video [video.find ('?v=')+3:].strip()
                if video_id not in prev_videos and video_id not in ytids:
                    ytids.append([video_id, "vid"])
    else:
        logger.debug(
            'List of videos not found. Please give the ID of videos in videos.txt file')

'''
    if os.path.exists('users.txt'):
        with open('users.txt') as f:
            for user in f:
                ytids.append([user.strip(), "forUsername"])
    else:
        logger.debug'List of users not found. Please give the list of users in users.txt file')
'''

# Function for retrieving the list of previously collected videos [allows resuming]
def getPreviousVideos(sourcedetails_collection,
                      activeprojectname):
    global prev_videos
    # if os.path.exists('youTubeLinks.tsv'):
    #     with open('youTubeLinks.tsv') as f:
    #         reader = csv.reader(f, delimiter='\t')
    #         for entry in reader:
    #             vid = entry[0]
    #             if vid != '' and vid != 'Video_ID' and vid not in prev_videos:
    #                 prev_videos.add(vid.strip())
    # else:
    #     meta_header = ['Video_ID', 'Channel_ID', 'Comment_ID',
    #                    'File_Name', 'Parent_ID', 'Date_Time_of_Retrieval']
    #     with open('youTubeLinks.tsv', 'w') as f:
    #         writer = csv.writer(f, delimiter='\t')
    #         writer.writerow(meta_header)
    aggregate_output = sourcedetails_collection.aggregate( [
                            {
                                "$match": {
                                    "projectname": activeprojectname,
                                            }
                            },
                            { 
                                "$sort" : {
                                    "lifesourceid" : 1
                                    }
                            },
                            {
                                "$project": {
                                    "_id": 0,
                                    "lifesourceid": 1
                                }
                            }
                            ])
    aggregate_output_list = []
    prev_videos = set()
    for doc in aggregate_output:
        logger.debug("aggregate_output: %s", pformat(doc))
        aggregate_output_list.append(doc)
        vid = doc['lifesourceid']
        if vid != '' and vid not in prev_videos:
            prev_videos.add(vid.strip())
    logger.debug('aggregate_output_list: %s', pformat(aggregate_output_list))
    logger.debug('prev_videos_aggregated: %s', pformat(prev_videos))

def run_youtube_crawler(projects_collection,
                            userprojects_collection,
                            sourcedetails_collection,
                            crawling_collection,
                            project_owner,
                            current_username,
                            active_project_name,
                            api_key,
                            data_links):
    #Get API Key for the User
    # getKey()
    global key
    key = api_key

    # Get list of already collected videos [will be skipped]
    getPreviousVideos(sourcedetails_collection,
                      active_project_name)
    logger.debug('prev_videos: %s', prev_videos)

    # Get list of channel / videos to retrieve data from
    # getList()
    global ytids
    global data_links_info

    if ('channels' in data_links):
        data_links_info = data_links['channels']
        channels = list(data_links['channels'].keys())
        for channel in channels:
            ytids.append([channel.strip(), "id"])

    if ('videos' in data_links):
        data_links_info = data_links['videos']
        videos = list(data_links['videos'].keys())
        for video in videos:
            video_id = video [video.find ('?v=')+3:].strip()
            if video_id not in prev_videos and video_id not in ytids:
                ytids.append([video_id, "vid"])
                data_links_info[video_id] = data_links_info[video]
                del data_links_info[video]

    # Set the count of videos already collected
    video_count = len(prev_videos)
    logger.debug('ytids: %s', ytids)
    logger.debug('video already collected: %s', video_count)
    logger.debug('new channels / videos to be collected: %s', len(ytids))

    # Creating XML directory
    # if not os.path.exists('xml-data-youtube'):
    #     os.makedirs('xml-data-youtube')

    # Creating CSV directory
    # if not os.path.exists('csv-data-youtube'):
    #     os.makedirs('csv-data-youtube')

    # Iterating through each channel / video
    for ytid, ytparam in ytids:
        urld = ''
        uploadid = ''
        if (ytid in data_links_info):
            search_keywords = data_links_info[ytid]
        else:
            search_keywords = []
        if ytparam == 'vid':
            getVideoData (projects_collection,
                            userprojects_collection,
                            sourcedetails_collection,
                            crawling_collection,
                            project_owner,
                            current_username,
                            active_project_name,
                            ytid,
                            search_keywords)
        else:
            try:
                urld = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&" + \
                    ytparam+"="+ytid+"&key="+key
                with urllib.request.urlopen(urld) as url:
                    datad = json.loads(url.read())
                uploadsdet = datad['items']
                # get upload id from channel id
                uploadid = uploadsdet[0]['contentDetails']['relatedPlaylists']['uploads']
            except Exception as e:
                logger.exception("")
                logger.debug('Exception: %s', e)
                logger.debug('Error in getting uploaded video set')
                logger.debug('urld: %s', urld)

            
            totalPages = 0
            totalResults = 0
            perPage = 0
            try:
                # retrieve list of videos
                if uploadid != '':
                    urld = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=50&playlistId="+uploadid+"&key="+key

                    with urllib.request.urlopen(urld) as url:
                        datad = json.loads(url.read())

                    # get data from first page of the video list
                    logger.debug('Getting videos for page 0 of channel: %s', ytid)
                    getAllVideosData(projects_collection,
                                        userprojects_collection,
                                        sourcedetails_collection,
                                        crawling_collection,
                                        project_owner,
                                        current_username,
                                        active_project_name,
                                        datad,
                                        search_keywords)
                    logger.debug('All videos on page 0 done')

                    # checking for more pages
                    totalResults = int(datad['pageInfo']['totalResults'])
                    perPage = int(datad['pageInfo']['resultsPerPage'])
                    totalPages = int(totalResults / perPage)
                    logger.debug('Total: %s pages of video in channel: %s', totalPages, ytid)
                    logger.debug('Per page: %s \tTotal Pages: %s \tTotal Results: %s', perPage, totalPages, totalResults)
            except Exception as e:
                logger.exception("")
                logger.debug(e)
                logger.debug('Error in getting videos on first page with upload id: %s', uploadid)
                logger.debug('urld: %s', urld)

            # Iterating through more pages
            if totalResults > 0 and totalResults > perPage:
                for i in range(totalPages):
                    #logger.debug('Page:', i)
                    #logger.debug(datad['pageInfo'])
                    if 'nextPageToken' in datad:
                        pToken = datad['nextPageToken']

                        # retrieve list from next pages
                        try:
                            urld = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=50&playlistId=" + \
                                uploadid+"&key="+key+"&pageToken="+pToken
                            with urllib.request.urlopen(urld) as url:
                                datad = json.loads(url.read())

                            # get data from next pages
                            logger.debug('Getting videos for page: %s of channel: %s',i, ytid)
                            getAllVideosData(projects_collection,
                                                userprojects_collection,
                                                sourcedetails_collection,
                                                crawling_collection,
                                                project_owner,
                                                current_username,
                                                active_project_name,
                                                datad,
                                                search_keywords)
                            logger.debug('All videos on page: %s', i, 'done')
                        except Exception as e:
                            logger.exception("")
                            logger.debug('Exception: %s', e)
                            logger.debug('urld: %s', urld)
                            logger.debug('Page: %s', i, 'out of total: %s', totalPages, 'pages of video')
                            logger.debug('Expected total videos: %s', totalResults)
                            logger.debug('Expected complete: %s', totalPages*50)
                            logger.debug('pToken: %s', pToken)
