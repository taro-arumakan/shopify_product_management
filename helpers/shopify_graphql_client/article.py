import logging

logger = logging.getLogger(__name__)


class Article:
    def blogs_by_query(self, query_string):
        query = """
        query blogsByQuery($query_string: String!) {
            blogs(first: 50, query: $query_string) {
                nodes {
                    id
                    handle
                    title
                    updatedAt
                    commentPolicy
                feed {
                    path
                    location
                }
                    createdAt
                    templateSuffix
                    tags
                }
            }
        }
        """
        variables = {"query_string": query_string}
        res = self.run_query(query, variables)
        return res["blogs"]["nodes"]

    def blog_id_by_blog_title(self, blog_title):
        blogs = self.blogs_by_query(f"title:'{blog_title.replace("'", "\\'")}'")
        if len(blogs) != 1:
            raise RuntimeError(
                f"{'Multiple' if blogs else 'No'} products found for {blog_title}: {blogs}"
            )
        return blogs[0]["id"]

    def articles_by_title(self, title):
        query = """
        query articlesByQuery($query_string: String!) {
            articles(first: 50, query: $query_string) {
                nodes {
                    id
                    handle
                    title
                    image {
                        altText
                        id
                        url
                    }
                    templateSuffix
                }
            }
        }
        """
        variables = {"query_string": f"title:'{title.replace("'", "\\'")}'"}
        res = self.run_query(query, variables)
        return res["articles"]["nodes"]

    def article_create(self, blog_title, title, template_suffix, media_url):
        blog_id = self.blog_id_by_blog_title(blog_title)
        query = """
        mutation CreateArticle($article: ArticleCreateInput!) {
            articleCreate(article: $article) {
                article {
                    id
                    title
                    author {
                        name
                    }
                    handle
                    body
                    summary
                    tags
                    image {
                        altText
                        url
                        id
                    }
                }
                userErrors {
                    code
                    field
                    message
                }
            }
        }
        """
        variables = {
            "article": {
                "blogId": blog_id,
                "title": title,
                "templateSuffix": template_suffix,
                "isPublished": True,
                "author": {"name": "Taro Nakamura"},
                "image": {"url": media_url, "altText": f"{title} cover image"},
            }
        }
        res = self.run_query(query, variables)
        if errors := res["articleCreate"]["userErrors"]:
            raise RuntimeError(f"Failed to create an article: {errors}")
        return res["articleCreate"]["article"]
