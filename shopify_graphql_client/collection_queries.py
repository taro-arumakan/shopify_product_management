class CollectionQueries:
    def products_by_collection_id(self, collection_id):
        query = '''
        query ProductsByCollection ($id: ID!) {
            collection(id: $id) {
                handle
                products(first: 50) {
                nodes {
                    title,
                    id,
                    status
                }
                }
            }
        }
        '''
        variables = {
            'id': collection_id
        }
        res = self.run_query(query, variables)
        return res['collection']['products']['nodes']

    def collection_id_by_title(self, title):
        query = '''
        query CustomCollectionList {
            collections(first: 50, query: "title:'%s'") {
                nodes {
                    id
                    handle
                    title
                    sortOrder
                    templateSuffix
                }
            }
        }''' % title
        res = self.run_query(query)
        if len(res['collections']['nodes']) != 1:
            raise RuntimeError(f"{'Multiple' if res['nodes'] else 'No'} collections found for {title}: {res['nodes']}")
        return res['collections']['nodes'][0]['id']
