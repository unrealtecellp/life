import json
import urllib.request
import datetime
# import arrow
import isodate
import xmltodict
import xml.etree.ElementTree as ET
from pytube import YouTube


def save_video_json(vlink, key):
    urlv = "https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id="+vlink+"&key="+key
    print('Url', urlv)
    fname = vlink+'.json'
    with urllib.request.urlopen(urlv) as url:
        datav = json.loads(url.read())
        print('Data fetched')
        data_obj = json.dumps(datav, indent=2, ensure_ascii=False)
        with open(fname, "w") as outfile:
            outfile.write(data_obj)


def save_search_json(api_key,
                     search_query,
                     video_count,
                     video_license):

    urld = "https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=" + \
        video_count+"&q="+search_query + \
        "&type=video&videoLicense="+video_license+"&key="+api_key
    print('Url', urld)
    fname = search_query+'_'+video_count+'_'+video_license+'.json'

    with urllib.request.urlopen(urld) as url:
        datad = json.loads(url.read())
        print('Data fetched')
        data_obj = json.dumps(datad, indent=2, ensure_ascii=False)
        with open(fname, "w") as outfile:
            outfile.write(data_obj)


def get_json_data(json_file, filetype):
    with open(json_file) as jf:
        jsond = json.load(jf)
    if filetype == 'video':
        all_itens = jsond['items']
        for item in all_itens:
            tags = item['snippet']['tags']
            duration = item['contentDetails']['duration']
            print('Duration', duration)
            # form_duration = datetime.datetime.fromisoformat(duration)
            form_duration = isodate.parse_duration(duration)
            print('Formatted', form_duration)
        print('Video tags', tags)
    elif filetype == 'search':
        all_links = []
        all_itens = jsond['items']
        for item in all_itens:
            link = item['id']['videoId']
            all_links.append(link)
        print('Search links', all_links)


def test_xml_to_json():
    video_tags = [
        "chili chicken recipes",
        "restaurant style chili chicken",
        "chili chicken in hindi",
        "chili chicken recipe bengali",
        "chilli chicken",
        "होटेल जैसा चिली चिकन",
        "chicken recipes",
        "chicken wings",
        "chicken pakora",
        "chicken fry",
        "chili chicken dry",
        "chicken biryani",
        "chicken curry",
        "chinese chilli chicken",
        "chicken leg piece",
        "chicken nuggets",
        "kfc chicken",
        "fried chicken",
        "roast chicken",
        "tandoori chicken",
        "chili chicken gravy",
        "chili chicken recipe ranveer brar",
        "chili paneer",
        "chicken",
        "dragon chicken"
    ]
    co3h = ET.Element('co3h')
    async_c = ET.SubElement(co3h, 'asynchronous')
    utube = ET.SubElement(async_c, 'youtube_video', {
        'id': str(video_count)})
    async_i = ET.SubElement(utube, 'async_info')
    for video_tag in video_tags:
        vtags = ET.SubElement(async_i, 'video_tags')
        # vtag = ET.SubElement(vtags, 'vtag')
        vtags.text = str(video_tag)

    doc = xmltodict.parse(ET.tostring(co3h))
    xml_to_json = json.dumps(doc, indent=2, ensure_ascii=False)
    # print('xml_to_json: %s', xml_to_json)
    xml_to_json = json.loads(xml_to_json)
    xml_to_json_data = xml_to_json["co3h"]["asynchronous"]["youtube_video"]
    async_info = xml_to_json_data["async_info"]
    print(async_info)


def downloadYoutubeAudio(video_link):
    try:
        print("Loading")
        yt = YouTube(video_link)
        print("filtering")
        # relevant_streams = yt.streams
        print("getting")
        download_stream = yt.streams.get_by_itag(140)
    except Exception as e:
        # logger.exception("")
        print("Exception", e)
        download_stream = ""
    return download_stream


if __name__ == '__main__':
    # api_key = 'AIzaSyDt5xEn8OzVHsfB9_s5TJDfSxwzswhVnYA' #GITHUB
    # api_key = 'AIzaSyBO3HIMZn3lgXC3MIQomKd-4RUYebcu96A' #riteshkrjnu
    # api_key = 'AIzaSyBxMeZQPMC9dmgwNzXjOz4A-LE2sErW5Ls' #riteshkr.kmi
    api_key = 'AIzaSyB3m8A-j9_4PGUg7N4dorhzZTG_i75PZeI'  # NPTEL SPOC
    search_query = 'agra'
    video_count = '10'
    video_license = 'creativeCommon'
    print('Going for topn')
    # save_search_json(api_key, search_query, video_count, video_license)

    print('Going for video')
    vlink = 'GC_DYsepAc8'
    # vlink = 'Ynz_fqTCuVw'
    # save_video_json(vlink, api_key)

    search_json = search_query+'_'+video_count+'_'+video_license+'.json'
    video_json = vlink+'.json'

    print('Loading search')
    # get_json_data(search_json, "search")
    # get_json_data(video_json, "video")

    # test_xml_to_json()
    vlink = 'https://www.youtube.com/watch?v=HJWCjeiv3mU'
    stream = downloadYoutubeAudio(vlink)
