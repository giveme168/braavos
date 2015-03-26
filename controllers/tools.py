# -*- coding: utf-8 -*-
import StringIO
import mimetypes

from flask import Response
from werkzeug.datastructures import Headers


def get_download_response(xls, filename):
    response = Response()
    response.status_code = 200
    output = StringIO.StringIO()
    xls.save(output)
    response.data = output.getvalue()
    mimetype_tuple = mimetypes.guess_type(filename)
    response_headers = Headers({
        'Pragma': "public",
        'Expires': '0',
        'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
        'Cache-Control': 'private',
        'Content-Type': mimetype_tuple[0],
        'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
        'Content-Transfer-Encoding': 'binary',
        'Content-Length': len(response.data)
    })
    response.headers = response_headers
    response.set_cookie('fileDownload', 'true', path='/')
    return response
