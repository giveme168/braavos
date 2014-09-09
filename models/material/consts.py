# -*- coding: UTF-8 -*-

IMAGE_HTML_TPL = """<!DOCTYPE html>
<html>
    <head>
        <base target="_blank">
        <style>
            * {{ margin: 0; padding: 0; border: 0; background:transparent }}
            body {{ overflow: hidden; font-family: Helvetica,Arial,sans-serif; }}
            a:link, a:visited, a:hover, a:active {{ color: #000; }}
        </style>
    </head>
    <body scroll="no">
        <a href="{click_link}" target="_blank">
            <img src="{image_link}" border="0" width="{width}" height="{height}">
        </a>
        <img src="{monitor_link}" border="0" width="0" height="0" style="position:absolute;">
        <img src="impression" border="0" width="0" height="0" style="position:absolute;">
    </body>
</html>
"""
