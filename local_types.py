import re
import json

WAVENUMBER_RE = re.compile(r"^\s*(\d+)(?:\s*-\s*(\d+))?\s*$")

class SpectralQuery:
    def __init__(self, queryargs):
        wavenumber = queryargs.get("wavenumber") # number or "number-number" (possible space)
        window_size = queryargs.get("window_size") # number
        keywords = queryargs.getlist("keywords[]")
        attributions = queryargs.getlist("attributions[]")
        species = queryargs.getlist("species[]")
        samples = queryargs.getlist("samples[]")
        metadata = queryargs.getlist("metadata[]")

        # ---
        
        if not wavenumber:
            raise ValueError("Missing wavenumber")

        wavenumber_match = WAVENUMBER_RE.match(wavenumber)

        if wavenumber_match:
            if wavenumber_match.group(2):
                low = min(wavenumber_match.group(1), wavenumber_match.group(2))
                high = max(wavenumber_match.group(1), wavenumber_match.group(2))
                wavenumber = (int(low), int(high))
            else:
                wavenumber = int(wavenumber_match.group(1))
        else:
            raise ValueError("Invalid wavenumber")
        
        try:
            error_margin = int(window_size) 
        except Exception:
            raise ValueError("Invalid window size")

        if not samples and not species:
            raise ValueError("Missing samples or species")

        # ---

        if isinstance(wavenumber, tuple):
            self.search_low = wavenumber[0] - error_margin
            self.search_high = wavenumber[1] + error_margin
        else:
            self.search_low = wavenumber - error_margin
            self.search_high = wavenumber + error_margin

        self.keywords = [keyword.lower().strip() for keyword in keywords]

        self.attributions = [attribution.lower().strip() for attribution in attributions]

        self.metadata = [metadatum.lower().strip() for metadatum in metadata]

        try:
            self.species = [int(specie) for specie in species]
        except Exception:
            raise ValueError("Invalid species")
        
        try:
            self.samples = [int(sample) for sample in samples]
        except Exception:
            raise ValueError("Invalid samples")


class SpectralQueryResponse():
    def __init__(self):
        self.bands = list()
        self.ranges = list()

    def add_band(self, article_id, position, attribution, sentence):
        self.bands.append((article_id, position, attribution, sentence))

    def add_range(self, article_id, start_position, end_position, attribution, sentence):
        self.ranges.append((article_id, start_position, end_position, attribution, sentence))

    def to_json(self):
        return json.dumps({
            "bands": [{
                "article_id": band[0],
                "position": band[1],
                "attribution": band[2],
                "sentence": band[3]
            } for band in self.bands],
            "ranges": [{
                "article_id": spec_range[0],
                "start": spec_range[1],
                "end": spec_range[2],
                "attribution": spec_range[3],
                "sentence": spec_range[4]
            } for spec_range in self.ranges]

        })
        
class ArticleQuery:
    def __init__(self, queryargs):
        serachterm = queryargs.get("article")

        if not serachterm:
            raise ValueError("Missing article")
        
        # If digit, pmcid
        try:
            self.article = int(serachterm)
        except Exception:
            self.article = serachterm

class ArticleQueryResponse():
    def __init__(self):
        self.articles = list()

    def add_article(self, article_id):
        self.articles.append(article_id)

    def to_json(self):
        return json.dumps({
            "articles": [{
                "article_id": article
            } for article in self.articles]
        })
    
class ArticleMetadataEntry():
    def __init__(self, umls_category_name, umls_entity_name, source_text):
        self.umls_category_name = umls_category_name
        self.umls_entity_name = umls_entity_name
        self.source_text = source_text

class ArticleSpectralBand():
    def __init__(self, position, attribution, sentence):
        self.position = position
        self.attribution = attribution
        self.sentence = sentence

class ArticleSpectralRange():
    def __init__(self, start_position, end_position, attribution, sentence):
        self.start_position = start_position
        self.end_position = end_position
        self.attribution = attribution
        self.sentence = sentence

class Article():
    def __init__(self, pmcid: int, title: str, hastables: bool, keywords: str, spectral_bands: list[ArticleSpectralBand], spectral_ranges: list[ArticleSpectralRange], metadata: list[ArticleMetadataEntry]):
        self.pmcid = pmcid
        self.title = title
        self.spectral_bands = spectral_bands
        self.spectral_ranges = spectral_ranges
        self.metadata = metadata
        self.hastables = hastables
        self.keywords = keywords