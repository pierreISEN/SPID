import sqlite3
from local_types import SpectralQueryResponse, ArticleQueryResponse, ArticleQuery, SpectralQuery, Article, ArticleMetadataEntry, ArticleSpectralBand, ArticleSpectralRange

class Database:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def get_full_article_info(self, pmcid):
        # Full article info is returned to the user when they click on an article in the search results

        title, hastables, keywords = self.conn.execute('''
            SELECT title, tables, GROUP_CONCAT(keyword, ', ') FROM Articles
            LEFT JOIN Keywords ON Articles.pmcid = Keywords.pmcid
            WHERE Articles.pmcid = ? GROUP BY Articles.pmcid
        ''', (pmcid,)).fetchone()

        hastables = bool(hastables)

        res = self.conn.execute('''
            SELECT UmlsCategories.name, UmlsEntities.name, term FROM ArticleMetadata
            JOIN UmlsCategories ON ArticleMetadata.umls_category_id = UmlsCategories.umls_category_id
            JOIN UmlsEntities ON ArticleMetadata.umls_entity_id = UmlsEntities.umls_entity_id
            WHERE pmcid = ?
        ''', (pmcid,)).fetchall()
        
        metadata = list()    

        for data in res:
            metadata.append(ArticleMetadataEntry(data[0], data[1], data[2]))

        res = self.conn.execute('''
            SELECT sentence, position, attribution FROM SpectralBands
            WHERE pmcid = ?
        ''', (pmcid,)).fetchall()

        bands = list()

        for band in res:
            bands.append(ArticleSpectralBand(band[1], band[2], band[0]))

        res = self.conn.execute('''
            SELECT sentence, start_position, end_position, attribution FROM SpectralRanges
            WHERE pmcid = ?
        ''', (pmcid,)).fetchall()

        spectral_ranges = list()

        for spec_range in res:
            spectral_ranges.append(ArticleSpectralRange(spec_range[1], spec_range[2], spec_range[3], spec_range[0]))

        return Article(pmcid, title, hastables, keywords, bands, spectral_ranges, metadata)

    def spectral_search(self, query: SpectralQuery):
        # Search for articles matching the query. Return a list of articles with their titles and keywords, as well as matching spectral bands and ranges

        positions_query = '''
            SELECT DISTINCT Articles.pmcid, Articles.title, position, attribution, sentence FROM Articles
            JOIN SpectralBands ON Articles.pmcid = SpectralBands.pmcid
            {join}
            WHERE position BETWEEN ? AND ? {where}
        '''

        ranges_query = '''
            SELECT Articles.pmcid, Articles.title, start_position, end_position, attribution, sentence FROM Articles
            JOIN SpectralRanges ON Articles.pmcid = SpectralRanges.pmcid
            {join}
            WHERE start_position BETWEEN ? AND ? AND end_position BETWEEN ? AND ? {where}
        '''

        params = []

        params_pos = [query.search_low, query.search_high]
        params_range = params_pos * 2

        joins = ""
        where = ""        

        if query.attributions:
            where += " AND  " + " OR ".join(["INSTR(LOWER(attribution), ?) > 0"] * len(query.attributions))
            params += query.attributions

        if query.keywords:
            where += " AND  (True AND " + " OR ".join(["INSTR(LOWER(Articles.title), ?) > 0"] * len(query.keywords))
            where += " OR  " + " OR ".join(["INSTR(LOWER(keyword), ?) > 0"] * len(query.keywords))
            where += ")"

            joins += " JOIN Keywords ON Articles.pmcid = Keywords.pmcid"
            params += query.keywords * 2

        if query.metadata:
            where += " AND Articles.pmcid IN (SELECT pmcid FROM ArticleMetadata JOIN UmlsEntities ON ArticleMetadata.umls_entity_id = UmlsEntities.umls_entity_id"
            where += " WHERE " + " OR ".join(["INSTR(LOWER(UmlsEntities.name), ?) > 0"] * len(query.metadata))
            where += " OR " + " OR ".join(["INSTR(LOWER(term), ?) > 0"] * len(query.metadata))
            where += ")"

            params += query.metadata * 2
            
        if query.species:
            where += " AND Articles.pmcid IN (SELECT pmcid FROM ArticleMetadata WHERE umls_category_id IN ({}))".format(",".join("?" * len(query.species)))
            params += query.species

        if query.samples:
            where += " AND Articles.pmcid IN (SELECT pmcid FROM ArticleMetadata WHERE umls_category_id IN ({}))".format(",".join("?" * len(query.samples)))
            params += query.samples

        bands = self.conn.execute(positions_query.format(join=joins, where=where), params_pos + params).fetchall()
        ranges = self.conn.execute(ranges_query.format(join=joins, where=where), params_range + params).fetchall()

        response = SpectralQueryResponse()

        for band in bands:
            response.add_band(str(band[0]) + " | " + str(band[1]), band[2], band[3], band[4])

        for spec_range in ranges:
            response.add_range(str(spec_range[0]) + " | " + str(spec_range[1]), spec_range[2], spec_range[3], spec_range[4], spec_range[5])

        return response.to_json()

    def article_search(self, query: ArticleQuery):
        # Search for articles matching the query. Return a list of articles with their titles
        if isinstance(query.article, str):
            sql_query = '''
                SELECT pmcid, title FROM Articles
                WHERE INSTR(LOWER(title), ?) > 0;
            '''
        else:
            sql_query = '''
                SELECT pmcid, title FROM Articles
                WHERE pmcid = ?;
            '''

        results = self.conn.execute(sql_query, (query.article,)).fetchall()

        response = ArticleQueryResponse()

        for result in results:
            response.add_article(str(result[0]) + " | " + result[1])

        return response.to_json()
    
