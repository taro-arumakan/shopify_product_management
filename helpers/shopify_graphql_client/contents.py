import logging

logger = logging.getLogger(__name__)


class Contents:

    def page_id_by_title(self, page_title):
        query = """
        query pageList($query_string: String!) {
            pages(first: 10, query: $query_string) {
                nodes {
                    id
                }
            }
        }
        """
        variables = {"query_string": f"title:{page_title}"}
        res = self.run_query(query, variables)
        if len(res["pages"]["nodes"]) != 1:
            raise RuntimeError(f"Error getting page id for {page_title}: {res}")
        return res["pages"]["nodes"][0]["id"]

    def create_url_redirect(self, from_path, to_path):
        for p in from_path, to_path:
            assert p.startswith(
                "/"
            ), "from and to paths starting with a leading slash relative to the top domain are expected"
        query = """
        mutation urlRedirectCreate($input: UrlRedirectInput!) {
            urlRedirectCreate(input: $input) {
                urlRedirect {
                    id
                    path
                    target
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        variables = {"input": {"path": from_path, "target": to_path}}
        res = self.run_query(query, variables)
        if res["urlRedirectCreate"]["userErrors"]:
            raise RuntimeError(
                f"Error creating URL redirect: {res['urlRedirectCreate']['userErrors']}"
            )
        return res["urlRedirectCreate"]["urlRedirect"]
