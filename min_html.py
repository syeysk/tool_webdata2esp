import lxml.html as html
#from lxml.html import html5parser as html

class MinHTML:
    
    def __init__(self):
        self.document = None

    def min(self, file_in, file_out, links=None, level=0):
        
        if level == 0:
            self.document = html.parse(file_in)
            el = self.document.getroot()
        else:
            el = file_in
        
        if len(el.getchildren()) > 0:
            for _el in el.getchildren():
                self.min(_el, file_out, links, level+1)
        else:
            if not isinstance(el.tag, str):
                el.getparent().remove(el) # remove html-comments
            elif el.tag == 'script' and 'src' in el.attrib and el.attrib['src']:
                if links is not None: links.append(el.attrib['src'])
            elif el.tag == 'link' and 'href' in el.attrib and el.attrib['href']:
                if links is not None: links.append(el.attrib['href'])
                
        if level == 0:
            self.document.write(file_out);