SITE_PAGES = {
    "page_1": {
        "method": "get",
        "url": "http://diamondsb.ag/",
    },
    "page_2": {
        "method": "post",
        "url": "http://diamondsb.ag/Login.aspx",
        "update_headers": {
            'Origin': 'http://diamondsb.ag',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Referer': 'http://diamondsb.ag/Themes/Theme001/Styles/btb.css?v=23',
            'Connection': 'keep-alive',
        },
        "post_data": [
            ('txtAccessOfCode', 'wine108'),
            ('txtAccessOfPassword', 'kt17'),
        ]
    }
}