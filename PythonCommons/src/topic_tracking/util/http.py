def detect_header_encoding(headers):
    return headers['content-type'].split('charset=')[-1]