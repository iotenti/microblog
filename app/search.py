from flask import current_app

# this is designed so it can be used in other apps

def add_to_index(index, model): #takes the sqlAlchemy model as second arg
    if not current_app.elasticsearch: #return nothing if Elasticsearch server is not configured
        return
    payload = {}
    for field in model.__searchable__: #__searchable__ from db post model
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, doc_type=index, id=model.id, body=payload) #use sqlAlchemy post id for id in elasticsearch

def remove_from_index(index, model): #takes the sqlAlchemy model as second arg
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)

def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search( #multi_match can search across multiple fields. fields = * searches in all fields, obv
        index=index, doc_type=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
        'from': (page - 1) * per_page, 'size': per_page}) #pagination math
    ids = [int(hit['_id']) for hit in search ['hits']['hits']] #list comprehension .. mmmmm
    return ids, search['hits']['total'] #return list of IDs