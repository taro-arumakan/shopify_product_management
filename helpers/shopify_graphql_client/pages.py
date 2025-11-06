class Pages:

    def pages_by_query(self, query_string, sort_key):
        query = """
        query pagesByQuery($query_string: String!, $sort_key: PageSortKeys!) {
            pages(first: 50, query: $query_string, sortKey: $sort_key) {
                nodes {
                    id
                    handle
                    title
                    createdAt
                    publishedAt
                    templateSuffix
                }
            }
        }
        """
        variables = {"query_string": query_string, "sort_key": sort_key}
        res = self.run_query(query, variables)
        return res["pages"]["nodes"]

    def pages_by_title(self, title, sort_key="PUBLISHED_AT"):
        if "*" in title:
            query_string = f"title:{title}"
        else:
            query_string = f"title:'{title.replace("'", "\\'")}'"
        return self.pages_by_query(query_string, sort_key)
