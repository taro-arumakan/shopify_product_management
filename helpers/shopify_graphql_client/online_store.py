import json
import re


class OnlineStore:

    def themes_by_names(self, names):
        query = """
        query themesByQuery($names: [String!]) {
            themes(first: 30, names: $names) {
                nodes {
                    name
                    id
                    role
                    prefix
                }
            }
        }
        """
        variables = {"names": names}
        res = self.run_query(query, variables)
        return res["themes"]["nodes"]

    def theme_json_to_dict(self, content):
        # Remove C-style comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        return json.loads(content)

    def current_theme(self):
        themes = self.themes_by_names("*")
        for theme in themes:
            if theme["role"] == "MAIN":
                return theme

    def current_color_swatch_config(self):
        theme = self.current_theme()
        setting_file = self.theme_file_by_theme_name_and_file_name(
            theme["name"], "config/settings_data.json"
        )
        return self.theme_json_to_dict(setting_file[0]["body"]["content"])["current"][
            "color_swatch_config"
        ]

    def theme_file_by_theme_name_and_file_name(self, theme_name, file_name):
        query = """
            query {
                themes(names:"%s" first:1) {
                    nodes {
                        files(filenames:"*%s*" first:50) {
                            nodes {
                                filename
                                body {
                                    ... on OnlineStoreThemeFileBodyText {
                                        content
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """ % (
            theme_name,
            file_name,
        )
        res = self.run_query(query)
        return res["themes"]["nodes"][0]["files"]["nodes"]

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

    def page_id_by_title(self, page_title):
        res = self.pages_by_title(page_title)
        if len(res) != 1:
            raise RuntimeError(f"Error getting page id for {page_title}: {res}")
        return res[0]["id"]

    def create_url_redirect(self, from_path, to_path):
        for p in from_path, to_path:
            assert p.startswith(
                "/"
            ), "from and to paths starting with a leading slash relative to the top domain are expected"
        query = """
        mutation urlRedirectCreate($input: UrlRedirectInput!) {
            urlRedirectCreate(urlRedirect: $input) {
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
