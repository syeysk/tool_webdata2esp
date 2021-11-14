import lxml.html as html


class MinHTML:
    def min(self, file_in, file_out, links=None, el=None):
        document = None
        if el is None:
            document = html.parse(file_in)
            el = document.getroot()

        for _el in el:
            self.min(file_in, file_out, links, _el)

        if el.text:
            el.text = el.text.strip()  # replace('\r', '')

        if el.tail:
            el.tail = el.tail.strip()  # replace('\r', '')

        if not isinstance(el.tag, str):
            el.getparent().remove(el)  # remove html-comments
        # elif links is not None:
        #     if el.tag == 'script' and el.attrib.get('src'):
        #         links.append(el.attrib['src'])
        #     elif el.tag == 'link' and el.attrib.get('href'):
        #         links.append(el.attrib['href'])
                
        if document:
            document.write(file_out, encoding='utf-8', method='html', pretty_print=False, strip_text=True)
