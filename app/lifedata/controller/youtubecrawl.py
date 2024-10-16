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
import io
import xmltodict
import isodate
from werkzeug.datastructures import FileStorage
# from pytube import YouTube
from pytubefix import YouTube
from pprint import pformat
import subprocess
from app.controller import (
    life_logging

)

from app.lifedata.controller import (
    save_crawled_data
)

from app.controller import (
    audiodetails,
    videodetails
)

from app.lifedata.transcription.controller import (
    transcription_audiodetails
)

logger = life_logging.get_logger()

key = ""

# List of channels : mention if you are pasting channel id or username - "id" or "forUsername"
# getVideoCount()

# ytids = [["bbcnews", "forUsername"], ["UCjq4pjKj9X4W9i7UnYShpVg", "id"]]
ytids = []
prev_videos = set()
csv_data = []
meta = []
video_count = 0
ccount = 0
crcount = 0
tccount = 0
data_links_info = {}
crawling_status = -1


def initialise_globals():
    global ytids
    global prev_videos
    global csv_data
    global meta
    global video_count
    global ccount
    global crcount
    global tccount
    global data_links_info
    global crawling_status

    ytids = []
    prev_videos = set()
    csv_data = []
    meta = []
    video_count = 0
    ccount = 0
    crcount = 0
    tccount = 0
    data_links_info = {}
    crawling_status = -1


def getAllCommentsData(utube, vlink, channel_id, cmntc, cc):
    # Comments on the video
    urlc = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId="+vlink+"&key="+key
    with urllib.request.urlopen(urlc) as url:
        datac = json.loads(url.read())

    # get comments from first page
    logger.debug('Video:\t:%s \tPage:\t1', video_count)
    utube = getCommentData(datac, utube, channel_id, vlink)

    # checking for more pages
    # totalResults = int(datac['pageInfo']['totalResults'])
    totalResults = int(cmntc)
    perPage = int(datac['pageInfo']['resultsPerPage'])
    totalPages = int(totalResults / perPage)
    logger.debug(
        'Total: %s pages of comments in video: %s', (totalPages+1), vlink)
    logger.debug('Per page: %s \tTotal Pages: %s \tTotal Results: %s',
                 perPage, (totalPages+1), totalResults)

    # Iterating through multiple pages of videos on the channel
    if totalResults > perPage:
        for i in range(totalPages):
            if 'nextPageToken' in datac:
                pToken = datac['nextPageToken']
                # logger.debug(pToken)
                urlc = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId=" + \
                    vlink+"&key="+key+"&pageToken="+pToken
                # logger.debug(urlc)
                try:
                    with urllib.request.urlopen(urlc) as url:
                        datac = json.loads(url.read())

                    # get data from next pages
                    logger.debug(
                        'Video:\t%s \tPage:\t%s', video_count, (i+2))
                    utube = getCommentData(
                        datac, utube, channel_id, vlink)

                except Exception as e:
                    logger.exception("")
                    logger.debug('Exception: %s', e)
                    logger.debug('urlc: %s', urlc)
                    logger.debug(
                        'Page: %s out of total: %s pages of comments', i, totalPages)
                    logger.debug(
                        'Expected total comments: %s', totalResults)
                    logger.debug(
                        'Total crawled comments: %s', ccount)
                    if ccount > 0:
                        logger.debug(
                            'The program will now exit after writing data from video: %s', video_count)
                        crawling_status = 0
                        break
                    else:
                        logger.debug(
                            'The program will now exit without writing data from video: %s', video_count)
                        quit(403)
            else:
                logger.debug(
                    'Video:\t%s \tPage:\t%s', video_count, (i+2))
                logger.debug('Total Comments:\t%s', tccount)
                logger.debug('No more next pages')
                if tccount != cmntc:
                    cc.text = str(tccount)
                break

    logger.debug(
        'Crawling complete. Now writing data and metadata to file')


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
        csv_data.append(['C' + str(video_count) + '.' +
                        str(ccount), html2text.html2text(final_text).strip()])

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
            logger.debug(
                'Video:\t%s \tComment:\t%s \tReplies on comment:\t%s', video_count, ccount, cid)
            for comment in replies_a:
                crcount += 1
                tccount += 1
                logger.debug('Video:\t%s \tComment:\t%s \tReply:\t%s',
                             video_count, ccount, crcount)
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


def downloadYoutubeVideo(video_link):
    try:
        logger.debug('Video Link %s', video_link)
        if '?v=' not in video_link:
            video_link = "https://www.youtube.com/watch?v="+video_link
        yt = YouTube(video_link)
        relevant_streams = yt.streams.filter(progressive=True)
        download_stream = relevant_streams.get_by_itag(22)
    except:
        logger.exception("")
        download_stream = ""
    return download_stream


def downloadYoutubeAudio(video_link):
    try:
        logger.debug('Video Link %s', video_link)
        if '?v=' not in video_link:
            video_link = "https://www.youtube.com/watch?v="+video_link
        yt = YouTube(video_link)
        relevant_streams = yt.streams.filter(only_audio=True)
        download_stream = relevant_streams.get_by_itag(140)
    except:
        logger.exception("")
        download_stream = ""
    return download_stream


def getAllVideosData(mongo, projects_collection,
                     userprojects_collection,
                     sourcedetails_collection,
                     crawling_collection,
                     project_owner,
                     current_username,
                     active_project_name,
                     datad,
                     search_keywords,
                     download_items,
                     save_format):
    for data in datad['items']:
        nlink = data['contentDetails']['videoId']
        getVideoData(mongo, projects_collection,
                     userprojects_collection,
                     sourcedetails_collection,
                     crawling_collection,
                     project_owner,
                     current_username,
                     active_project_name,
                     nlink,
                     search_keywords,
                     download_items,
                     save_format)


def getVideoData(mongo, projects_collection,
                 userprojects_collection,
                 sourcedetails_collection,
                 crawling_collection,
                 project_owner,
                 current_username,
                 active_project_name,
                 vlink,
                 search_keywords,
                 download_items,
                 save_format):
    global ccount
    global crcount
    global video_count
    global meta
    global csv_data
    global tccount
    global crawling_status

    if vlink not in prev_videos:
        csv_data.clear()
        meta.clear()

        # Getting Video Data
        # ntitle = data['snippet']['title']
        urlv = "https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id="+vlink+"&key="+key
        with urllib.request.urlopen(urlv) as url:
            datav = json.loads(url.read())
            # logger.debugdatav)
        try:
            for vdata in datav['items']:
                # Checking if the video has comments
                stats = vdata['statistics']
                cmntc = '0'
                if 'commentCount' in stats:
                    cmntc = stats['commentCount']
                logger.debug('Total comments on video: %s : %s', vlink, cmntc)
                # Proceeding further if there are comments on video
                # if int(cmntc) > 0:
                logger.debug('Getting metadata of video: %s', vlink)
                video_details = vdata['contentDetails']
                duration = video_details['duration']
                formatted_duration = isodate.parse_duration(duration)

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

                video_tags = []
                if 'tags' in metadata:
                    video_tags = metadata['tags']

                video_id = vlink
                vLink = "https://www.youtube.com/watch?v="+vlink

                # Increasing file count
                video_count += 1

                # Adding for CSV File
                csv_data.append(
                    ['Youtube Corpus ' + str(video_count), vLink])

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
                pub = ET.SubElement(async_i, 'publisher_id')
                pub.text = str(channel_id)
                ttl = ET.SubElement(async_i, 'video_title')
                ttl.text = str(title)
                desc = ET.SubElement(async_i, 'video_description')
                desc.text = html2text.html2text(str(description)).strip()
                dat = ET.SubElement(async_i, 'published_date')
                dat.text = str(date)
                tm = ET.SubElement(async_i, 'published_time')
                tm.text = str(time)
                vws = ET.SubElement(async_i, 'total_views')
                vws.text = str(views)
                lks = ET.SubElement(async_i, 'video_likes')
                lks.text = str(likes)
                dlks = ET.SubElement(async_i, 'video_dislikes')
                dlks.text = str(dislikes)
                fav = ET.SubElement(async_i, 'video_favourites')
                fav.text = str(favs)
                cc = ET.SubElement(async_i, 'total_comments')
                cc.text = str(cmntc)
                lng = ET.SubElement(async_i, 'audio_language')
                lng.text = str(lang)
                dur = ET.SubElement(async_i, 'video_duration')
                dur.text = str(formatted_duration)
                # vtags = ET.SubElement(async_i, 'video_tags')
                if len(video_tags) > 0:
                    for video_tag in video_tags:
                        # vtag = ET.SubElement(vtags, 'vtag')
                        vtags = ET.SubElement(async_i, 'video_tags')
                        vtags.text = str(video_tag)
                else:
                    vtags = ET.SubElement(async_i, 'video_tags')
                    vtags.text = ""

                # crawl date time
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                acc_dt = ET.SubElement(async_i, 'accessed_at')
                acc_dt.text = str(dt_string)

                main = ET.SubElement(utube, 'main_content')
                org = ET.SubElement(
                    main, 'original_script', {'name': 'Roman'})
                org.text = str(vLink)

                write_data = False
                # Get Audio and Video
                if 'audio' in download_items:
                    logger.debug('Downloading audio of video: %s', vlink)
                    audio_stream = downloadYoutubeAudio(
                        vlink)
                    logger.debug('audio_stream: %s', audio_stream)
                    logger.debug('audio_stream: %s', type(audio_stream))
                    if audio_stream != '':
                        write_data = True
                else:
                    audio_stream = ''

                if 'video' in download_items:
                    logger.debug('Downloading video of video: %s', vlink)
                    video_stream = downloadYoutubeVideo(
                        vlink)
                    if video_stream != '':
                        write_data = True
                else:
                    video_stream = ''

                # Get comments
                if 'comments' in download_items and int(cmntc) > 0:
                    crawling_status = 1
                    logger.debug('Downloading comments of video: %s', vlink)
                    # Metadata for this video
                    meta_video = []
                    meta_video.append(vlink)  # video ID
                    meta_video.append(channel_id)  # channel ID
                    meta_video.append('NA')  # comment ID
                    meta_video.append('youtube_corpus_' +
                                      str(video_count))  # file name
                    meta_video.append('NA')  # parent_ID
                    meta_video.append(dt_string)  # current date time
                    meta.append(meta_video)

                    getAllCommentsData(utube,
                                       vlink,
                                       channel_id,
                                       cmntc,
                                       cc)
                    write_data = True

                if write_data:
                    logger.debug('Writing data of video: %s', vlink)
                    write_crawled_data(mongo, co3h,
                                       projects_collection,
                                       userprojects_collection,
                                       sourcedetails_collection,
                                       crawling_collection,
                                       project_owner,
                                       current_username,
                                       active_project_name,
                                       vlink,
                                       search_keywords,
                                       save_format,
                                       audio_stream,
                                       video_stream,
                                       download_items)
        except Exception:
            # traceback.logger.debugexc()
            logger.exception("")
            with open('linksnotparse.txt', 'a') as notparse:
                notparse.write("https://www.youtube.com/watch?v="+vlink+"\n")


def write_metadata_file():
    # Writing metadata file
    with open('youTubeLinks.tsv', 'a') as f_w:
        writer = csv.writer(f_w, delimiter='\t')
        writer.writerows(meta)


def write_xml_file(co3h, fname):
    # XML to String
    complete = ET.tostring(co3h)
    complete = minidom.parseString(
        ET.tostring(co3h)).toprettyxml(indent="   ")

    # Writing XML File
    with open('xml-data-youtube/' + fname + '.xml', 'w') as f_w:
        f_w.write(complete)
    logger.debug('xml-data-youtube: %s', complete)


def get_mongodb_json(co3h):
    # with open('xml-data-youtube/' + fname + '.xml', 'r') as f_r:
    #     doc = xmltodict.parse(f_r.read())
    # xml_to_json = json.dumps(doc, indent=2, ensure_ascii=False)
    # logger.debug('xml_to_json: %s', xml_to_json)
    try:
        doc = xmltodict.parse(ET.tostring(co3h))
        xml_to_json = json.dumps(
            doc, indent=2, ensure_ascii=False)
        logger.debug('xml_to_json TYPE: %s', type(xml_to_json))
        logger.debug('xml_to_json: %s', xml_to_json)
        xml_to_json = json.loads(xml_to_json)
        # logger.debug('xml_to_json: %s', pformat(xml_to_json))
        # logger.debug('xml_to_json TYPE: %s', type(xml_to_json))
        # logger.debug('co3h TYPE: %s', type(co3h))
        # logger.debug('co3h: %s', co3h)
        logger.debug('csv-data-youtube: %s', csv_data)

        logger.debug('youTubeLinks.tsv: %s', meta)
    except:
        logger.exception("")

    return xml_to_json


def write_csv_file(fname):
    # Writing CSV File
    with open('csv-data-youtube/' + fname + '.csv', 'w') as f_w:
        writer = csv.writer(f_w, delimiter='\t')
        writer.writerows(csv_data)


def write_audio_video_file(audio_video_stream):
    return True


def write_mongodb_audio(mongo,
                        projects,
                        userprojects,
                        crawling,
                        projectowner,
                        activeprojectname,
                        current_username,
                        speakerId,
                        audio_stream):
    new_audio_file = {}

    logger.debug('audio_stream.title: %s',
                 audio_stream.title)
    logger.debug('filesize_mb: %s',
                 audio_stream.filesize_mb)


    string_file_name = audio_stream.title
    string_file_name = re.sub(r'[^A-Za-z0-9]+', '_', string_file_name)
    # logger.debug('string_file_name: %s', string_file_name)
    # file_name = string_file_name[:15]+'_'+speakerId+'_audio.mp4'
    download_file_name = string_file_name[:15]+'_'+speakerId+'_audio.mp4'
    # download_file_name = download_file_name.replace(' ', '_')
    # logger.debug('download_file_name: %s', download_file_name)
    file_name = download_file_name.replace('.mp4', '.wav')
    # logger.debug('file_name: %s', file_name)
    audio_stream_file_path = audio_stream.download(filename=download_file_name,
                                                   skip_existing=False)
    # logger.debug('audio_stream: %s', type(audio_stream))
    # logger.debug('audio_stream_file_path: %s', audio_stream_file_path)
    wav_audio_stream_folder_path = '/'.join(audio_stream_file_path.split('/')[1:-1])
    wav_audio_stream_file_path = os.path.join(wav_audio_stream_folder_path, file_name)
    # logger.debug('wav_audio_stream_file_path: %s', wav_audio_stream_file_path)
    convert_to_wav_command = ['ffmpeg', '-y', '-i', download_file_name, file_name]
    subprocess.run(convert_to_wav_command)


    # file_content = io.BytesIO()
    # audio_stream.stream_to_buffer(file_content)
    # logger.debug ("File content: %s", file_content)

    with open('/'+wav_audio_stream_file_path, 'rb') as f:
        file_content = io.BytesIO(f.read())

    # logger.debug ("Upload type", fileType)
    new_audio_file['audiofile'] = FileStorage(
        file_content, filename=file_name, content_type='audio/x-wav')
    logger.debug('audio_stream: %s', type(audio_stream))
    logger.debug(new_audio_file)
    os.remove(download_file_name)
    os.remove(file_name)
    # file_state, transcription_doc_id, fs_file_id = audiodetails.saveoneaudiofile(mongo,
    #                                                                              projects,
    #                                                                              userprojects,
    #                                                                              crawling,
    #                                                                              projectowner,
    #                                                                              activeprojectname,
    #                                                                              current_username,
    #                                                                              speakerId,
    #                                                                              new_audio_file,
    #                                                                              run_vad=False,
    #                                                                              run_asr=False,
    #                                                                              get_audio_json=False)
    
    file_state, transcription_doc_id, fs_file_id = transcription_audiodetails.saveoneaudiofile(mongo,
                                                                                 projects,
                                                                                 userprojects,
                                                                                 crawling,
                                                                                 projectowner,
                                                                                 activeprojectname,
                                                                                 current_username,
                                                                                 speakerId,
                                                                                 new_audio_file,
                                                                                 run_vad=True,
                                                                                 run_asr=False,
                                                                                 get_audio_json=True)
    
    audio_doc_id = transcription_doc_id[0].inserted_id
    # logger.debug("audio_doc_id: %s", audio_doc_id)
    updated_filename = crawling.find_one(
        {
            '_id': audio_doc_id,
            'projectname': activeprojectname,
            # 'username': current_username,
            'speakerId': speakerId,
            'dataType': "audio"
        },
        {
            'audioFilename': 1,
            '_id': 0
        }
    )['audioFilename']
    # logger.debug('transcription_doc_id: %s, fs_file_id: %s, updated_filename: %s, file_state: %s',
    #              transcription_doc_id, fs_file_id, updated_filename, file_state)
    return transcription_doc_id, fs_file_id, updated_filename, file_state


def write_mongodb_video(mongo,
                        projects,
                        userprojects,
                        crawling,
                        projectowner,
                        activeprojectname,
                        current_username,
                        speakerId,
                        video_stream):

    new_video_file = {}
    string_file_name = video_stream.title
    file_name = string_file_name[:15]+'_'+speakerId+'_video.mp4'

    file_content = io.BytesIO()
    video_stream.stream_to_buffer(file_content)
    # logger.debug ("File content", file_content)
    # logger.debug ("Upload type", fileType)
    new_video_file['videofile'] = FileStorage(
        file_content, filename=file_name)
    file_state, transcription_doc_id, fs_file_id = videodetails.saveonevideofile(mongo,
                                                                                 projects,
                                                                                 userprojects,
                                                                                 crawling,
                                                                                 projectowner,
                                                                                 activeprojectname,
                                                                                 current_username,
                                                                                 speakerId,
                                                                                 new_video_file,
                                                                                 run_vad=False,
                                                                                 run_asr=False,
                                                                                 get_audio_json=False)

    updated_filename = crawling.find_one(
        {'projectname': activeprojectname,
            'username': current_username, 'speakerId': speakerId, 'dataType': "video"},
        {'videoFilename': 1, '_id': 0})['videoFilename']
    return transcription_doc_id, fs_file_id, updated_filename, file_state


def write_crawled_data(mongo, co3h,
                       projects_collection,
                       userprojects_collection,
                       sourcedetails_collection,
                       crawling_collection,
                       project_owner,
                       current_username,
                       active_project_name,
                       vlink,
                       search_keywords,
                       save_format,
                       audio_stream,
                       video_stream,
                       download_items):

    logger.debug("Save format: %s \t Download items %s",
                 save_format, download_items)
    audio_doc_id = fs_audio_id = audio_filename = ''
    video_doc_id = fs_video_id = video_filename = ''

    if 'xml' in save_format or 'csv' in save_format:
        if 'comments' in download_items:
            # File Name
            fname = 'youtube_corpus_'+str(video_count)
            write_metadata_file()

            if 'xml' in save_format:
                write_xml_file(co3h, fname)

            elif 'csv' in save_format:
                write_csv_file(fname)

        if 'audio' in download_items:
            write_audio_video_file(audio_stream)

        if 'video' in download_items:
            write_audio_video_file(video_stream)

    if 'mongodb' in save_format:
        if 'audio' in download_items:
            logger.debug('Writing audio of video: %s to mongodb', vlink)
            # new_audio_file = {}
            # file_content = io.BytesIO()
            # audio_stream.stream_to_buffer(file_content)
            # file_name = audio_stream.title
            # if len(file_name) > 10:
            #     file_name = file_name[:10]
            #     file_name = file_name.replace(' ', '_')

            # new_audio_file['audiofile'] = FileStorage(
            #                 file_content, filename=file_name)
            audio_doc_id, fs_audio_id, audio_filename, file_state = write_mongodb_audio(mongo,
                                                                                        projects_collection,
                                                                                        userprojects_collection,
                                                                                        crawling_collection,
                                                                                        project_owner,
                                                                                        active_project_name,
                                                                                        current_username,
                                                                                        vlink,
                                                                                        audio_stream)
            audio_doc_id = audio_doc_id[0].inserted_id

        if 'video' in download_items:
            logger.debug('Writing video of video: %s to mongodb', vlink)
            video_doc_id, fs_video_id, video_filename, file_state = write_mongodb_video(mongo,
                                                                                        projects_collection,
                                                                                        userprojects_collection,
                                                                                        crawling_collection,
                                                                                        project_owner,
                                                                                        active_project_name,
                                                                                        current_username,
                                                                                        vlink,
                                                                                        video_stream)
            video_doc_id = video_doc_id.inserted_id

        # if 'comments' in download_items:
        logger.debug("Getting data JSON for writing to mongodb")
        xml_to_json = get_mongodb_json(co3h)

        logger.debug('Writing all data of video: %s to mongodb', vlink)
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
                                                    search_keywords,
                                                    fs_audio_id,
                                                    audio_filename,
                                                    fs_video_id,
                                                    video_filename,
                                                    audio_doc_id,
                                                    video_doc_id,
                                                    crawling_status)


# Function for retrieving the API key


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
                video_id = video[video.find('?v=')+3:].strip()
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
                      activeprojectname, save_format):
    global prev_videos

    if 'xml' in save_format or 'csv' in save_format:
        if os.path.exists('youTubeLinks.tsv'):
            with open('youTubeLinks.tsv') as f:
                reader = csv.reader(f, delimiter='\t')
                for entry in reader:
                    vid = entry[0]
                    if vid != '' and vid != 'Video_ID' and vid not in prev_videos:
                        prev_videos.add(vid.strip())
        else:
            meta_header = ['Video_ID', 'Channel_ID', 'Comment_ID',
                           'File_Name', 'Parent_ID', 'Date_Time_of_Retrieval']
            with open('youTubeLinks.tsv', 'w') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(meta_header)
    elif 'mongodb' in save_format:
        aggregate_output = sourcedetails_collection.aggregate([
            {
                "$match": {
                    "projectname": activeprojectname,
                }
            },
            {
                "$sort": {
                    "lifesourceid": 1
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
        logger.debug('aggregate_output_list: %s',
                     pformat(aggregate_output_list))
        logger.debug('prev_videos_aggregated: %s', pformat(prev_videos))


def run_youtube_crawler(mongo, projects_collection,
                        userprojects_collection,
                        sourcedetails_collection,
                        crawling_collection,
                        project_owner,
                        current_username,
                        active_project_name,
                        api_key,
                        data_links,
                        download_items=['comments'],
                        save_formats=['mongodb']):
    # Get API Key for the User
    # getKey()
    initialise_globals()

    global key
    key = api_key

    # Get list of already collected videos [will be skipped]
    getPreviousVideos(sourcedetails_collection,
                      active_project_name, save_formats)
    logger.debug('prev_videos: %s', prev_videos)

    # Get list of channel / videos to retrieve data from
    # getList()
    global ytids
    global data_links_info

    ytids = []
    crawled_video_ids = []

    if ('channels' in data_links):
        data_links_info = data_links['channels']
        channels = list(data_links['channels'].keys())
        for channel in channels:
            ytids.append([channel.strip(), "id"])

    if ('videos' in data_links or 'topn' in data_links):
        if 'videos' in data_links:
            data_search_criteria = 'videos'
        elif 'topn' in data_links:
            data_search_criteria = 'topn'

        data_links_info = data_links[data_search_criteria]
        videos = list(data_links[data_search_criteria].keys())
        for video in videos:
            video_id = video[video.find('?v=')+3:].strip()
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
            getVideoData(mongo, projects_collection,
                         userprojects_collection,
                         sourcedetails_collection,
                         crawling_collection,
                         project_owner,
                         current_username,
                         active_project_name,
                         ytid,
                         search_keywords,
                         download_items,
                         save_formats)
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
                    logger.debug(
                        'Getting videos for page 0 of channel: %s', ytid)
                    getAllVideosData(mongo, projects_collection,
                                     userprojects_collection,
                                     sourcedetails_collection,
                                     crawling_collection,
                                     project_owner,
                                     current_username,
                                     active_project_name,
                                     datad,
                                     search_keywords,
                                     download_items,
                                     save_formats)
                    logger.debug('All videos on page 0 done')

                    # checking for more pages
                    totalResults = int(datad['pageInfo']['totalResults'])
                    perPage = int(datad['pageInfo']['resultsPerPage'])
                    totalPages = int(totalResults / perPage)
                    logger.debug(
                        'Total: %s pages of video in channel: %s', totalPages, ytid)
                    logger.debug(
                        'Per page: %s \tTotal Pages: %s \tTotal Results: %s', perPage, totalPages, totalResults)
            except Exception as e:
                logger.exception("")
                logger.debug(e)
                logger.debug(
                    'Error in getting videos on first page with upload id: %s', uploadid)
                logger.debug('urld: %s', urld)

            # Iterating through more pages
            if totalResults > 0 and totalResults > perPage:
                for i in range(totalPages):
                    # logger.debug('Page:', i)
                    # logger.debug(datad['pageInfo'])
                    if 'nextPageToken' in datad:
                        pToken = datad['nextPageToken']

                        # retrieve list from next pages
                        try:
                            urld = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=50&playlistId=" + \
                                uploadid+"&key="+key+"&pageToken="+pToken
                            with urllib.request.urlopen(urld) as url:
                                datad = json.loads(url.read())

                            # get data from next pages
                            logger.debug(
                                'Getting videos for page: %s of channel: %s', i, ytid)
                            getAllVideosData(mongo, projects_collection,
                                             userprojects_collection,
                                             sourcedetails_collection,
                                             crawling_collection,
                                             project_owner,
                                             current_username,
                                             active_project_name,
                                             datad,
                                             search_keywords,
                                             download_items,
                                             save_formats)
                            logger.debug('All videos on page: %s', i, 'done')
                        except Exception as e:
                            logger.exception('Exception: %s', e)
                            logger.debug('Exception: %s', e)
                            logger.debug('urld: %s', urld)
                            logger.debug(
                                'Page: %s', i, 'out of total: %s', totalPages, 'pages of video')
                            logger.debug(
                                'Expected total videos: %s', totalResults)
                            logger.debug(
                                'Expected complete: %s', totalPages*50)
                            logger.debug('pToken: %s', pToken)
        crawled_video_ids.append(ytid)
        # logger.debug("crawled_video_ids: %s", crawled_video_ids)

    return crawled_video_ids


# Get link to top n videos for the given search query
def get_topn_videos(api_key,
                    search_query,
                    video_count,
                    video_license):
    all_links = []

    urld = "https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=" + \
        video_count+"&q="+search_query + \
        "&type=video&videoLicense="+video_license+"&key="+api_key

    with urllib.request.urlopen(urld) as url:
        datad = json.loads(url.read())

    all_itens = datad['items']
    for item in all_itens:
        vid = item['id']['videoId']
        link = 'https://www.youtube.com/watch?v='+str(vid)
        all_links.append(link)

    return all_links
