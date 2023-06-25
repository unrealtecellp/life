import io
import zipfile
import zlib
import time
import os
from flask import Flask, request, send_file, make_response

@app.route('/download', methods=['GET','POST'])
def download():     
    fileobj = io.BytesIO()
    with zipfile.ZipFile(fileobj, 'w') as zip_file:
        zip_info = zipfile.ZipInfo(FILEPATH)
        zip_info.date_time = time.localtime(time.time())[:6]
        zip_info.compress_type = zipfile.ZIP_DEFLATED
        with open(FILEPATH, 'rb') as fd:
            zip_file.writestr(zip_info, fd.read())
    fileobj.seek(0)

    response = make_response(fileobj.read())
    response.headers.set('Content-Type', 'zip')
    response.headers.set('Content-Disposition', 'attachment', filename='%s.zip' % os.path.basename(FILEPATH))
    return response

def method2():
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        files = result['files']
        for individualFile in files:
            data = zipfile.ZipInfo(individualFile['fileName'])
            data.date_time = time.localtime(time.time())[:6]
            data.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(data, individualFile['fileData'])
    memory_file.seek(0)
    return send_file(memory_file, attachment_filename='capsule.zip', as_attachment=True)


#Method 3

from flask import Response
import requests
import zipstream 

# we need a generator to handle the data from the file
def _generator(photo_url):
    # download a file and stream it
    r = requests.get(photo_url, stream=True)
    if r.status_code != 200:
        return
    for chunk in r.iter_content(1024):
        yield chunk


def generate_zip():
    compressor = zlib.compressobj()
    for x in range(10000):
        chunk = compressor.compress(f"this is my line: {x}\n".encode())
        if chunk:
            yield chunk
    yield compressor.flush()

@app.route('/package.zip', methods=['GET'], endpoint='zipball')
def zipball():
    def generator():
        z = zipstream.ZipFile(mode='w', compression=ZIP_DEFLATED)

        z.write_iter("path/to/file", _generator("http://i.imgur.com/9DpELbT.jpg"))
        z.write_iter("path/to/file1", _generator("http://i.imgur.com/uAWnH3S.jpg"))
        # add all the necessary files here
        z.write_iter("path/to/file2", _generator("http://i.imgur.com/Phhjhbn.png"))

        # here is where the magic happens. Each call will iterate the generator we wrote for each file
        # one at a time until all files are completed.
        for chunk in z:
            yield chunk

    response = Response(generator(), mimetype='application/zip')
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format('files.zip')
    return response