from bs4 import BeautifulSoup, NavigableString


def html_to_json(html):
    soup = BeautifulSoup(html, 'html.parser')
    return _element_to_json(soup)


def _element_to_json(element):
    if isinstance(element, str):
        return {'text': element.strip()}

    if element.name == '[document]':
        result = []
        for child in element.children:
            child_json = _element_to_json(child)
            if child_json:
                result.append(child_json)

        if len(result) == 1:
            return result[0]

        return result or None

    result = {'tag': element.name}

    if element.attrs:
        result['attributes'] = element.attrs

    children = []
    for child in element.children:
        child_json = _element_to_json(child)
        if child_json:
            children.append(child_json)

    if children:
        result['children'] = children

    return result


def json_to_html(json_data):
    soup = BeautifulSoup('', 'html.parser')
    element = _json_to_element(json_data, soup)
    return str(element)


def _json_to_element(json_data, soup):
    if 'text' in json_data:
        return NavigableString(json_data['text'])

    if 'tag' in json_data:
        tag_name = json_data['tag']
        attrs = json_data.get('attributes', {})
        element = soup.new_tag(tag_name, **attrs)

        for child_json in json_data.get('children', []):
            child_element = _json_to_element(child_json, soup)
            element.append(child_element)

        return element

    return ''
