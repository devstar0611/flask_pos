from selectorlib import Extractor
yaml_string = """
    title:
        css: "h1"
        type: Text
    link:
        css: "h2 a"
        type: Link
    """
extractor = Extractor.from_yaml_string(yaml_string)
html = """
    <h1>Title</h1>
    <h2>Usage
        <a class="headerlink" href="http://test">¶</a>
    </h2>
    """
extractor.extract(html)
{'title': 'Title', 'link': 'http://test'}