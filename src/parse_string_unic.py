def parse_string_with_unicode(s):
    # Disclaimer: ChatGPT-generated portion of code, made when I was but a wee rookie
    parsed_string = list()
    i = 0
    while i < len(s):
        if ord(s[i]) >= 65536:
            parsed_string.append(s[i:i+1])
        else:
            parsed_string.append(s[i])
        i += 1
    return parsed_string