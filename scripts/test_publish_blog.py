"""Behavior checks run against isolated sites, never the checked-in portfolio."""

import json
from html.parser import HTMLParser
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest

from publish_blog import GENERATED, PREVIEW_END, PREVIEW_START, publish


BODY = '\n<h2>A section</h2>\n<p>Repository-authored HTML.</p>\n'
HOMEPAGE = '''<!doctype html>
<html lang="en"><head><title>Portfolio</title></head><body>
<header class="site-header">
  <a class="site-brand" href="#top">Alexey Zarakovskiy</a>
  <nav class="primary-nav"><a href="#projects">Projects</a><a href="#personal">Personal</a><a href="blog/">Blog</a></nav>
  <a class="resume-link" href="resume/">Résumé</a>
  <a href="#contact" data-contact="github">GitHub</a>
  <a href="#contact" data-contact="email">Contact</a>
  <span class="header-section" aria-hidden="true"></span>
</header>
<main id="main"><p>Unchanged content before.</p>
<!-- blog-preview:start -->
<!-- blog-preview:end -->
<p>Unchanged content after.</p></main><script>homepageOnly();</script>
</body></html>
'''


class Links(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))


class PublishBlogTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "posts").mkdir()
        (self.root / "index.html").write_text(HOMEPAGE, encoding="utf-8")
        self.metadata = {
            "title": "A technical note",
            "date": "2026-10-18",
            "tags": ["Python", "Static sites"],
            "summary": "A short description.",
        }

    def post(self, slug, body=BODY, **overrides):
        metadata = dict(self.metadata, title=slug.title())
        metadata.update(overrides)
        path = self.root / "posts" / f"{slug}.html"
        path.write_text("<!--\n" + json.dumps(metadata) + "\n-->" + body, encoding="utf-8")
        return path

    def read(self, path):
        return (self.root / path).read_text(encoding="utf-8")

    def post_links(self, page):
        return [link for link in Links(page).links
                if link.get("aria-label", "").startswith("Read post: ")]

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def test_empty_site_preserves_homepage_and_repeated_output(self):
        publish(self.root)
        home = self.read("index.html")
        listing = self.read("blog/index.html")
        self.assertFalse(home.partition(PREVIEW_START)[2].partition(PREVIEW_END)[0].strip())
        normalized_home = home.replace('href="blog/" hidden', 'href="blog/"')
        self.assertEqual(normalized_home.partition(PREVIEW_START)[0],
                         HOMEPAGE.partition(PREVIEW_START)[0])
        self.assertEqual(home.partition(PREVIEW_END)[2], HOMEPAGE.partition(PREVIEW_END)[2])
        for page, blog_href, non_blog_hrefs in (
            (home, "blog/", ["#top", "#projects", "#personal", "resume/",
                             "#contact", "#contact"]),
            (listing, "./", ["../index.html#top", "../index.html#projects",
                             "../index.html#personal", "../resume/",
                             "../index.html#contact", "../index.html#contact"]),
        ):
            header = re.search(r'<header class="site-header">.*?</header>', page, re.DOTALL)[0]
            links = Links(header).links
            blog_links = [link for link in links if link["href"] == blog_href]
            self.assertEqual(len(blog_links), 1)
            self.assertIn("hidden", blog_links[0])
            self.assertEqual([link["href"] for link in links if link["href"] != blog_href],
                             non_blog_hrefs)
            self.assertFalse(self.post_links(page))
        before = self.snapshot()
        publish(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_first_post_and_last_deletion_restore_preview_and_navigation(self):
        publish(self.root)
        empty = self.snapshot()
        publish(self.root)
        self.assertEqual(self.snapshot(), empty)

        source = self.post("first")
        publish(self.root)
        home = self.read("index.html")
        listing = self.read("blog/index.html")
        article = self.read("blog/first/index.html")
        self.assertIn('id="blog"', home)
        self.assertEqual([link["href"] for link in self.post_links(home)], ["blog/first/"])
        self.assertEqual([link["href"] for link in self.post_links(listing)], ["first/"])
        for page, blog_href in ((home, "blog/"), (listing, "./"), (article, "../")):
            header = re.search(r'<header class="site-header">.*?</header>', page, re.DOTALL)[0]
            blog_links = [link for link in Links(header).links if link["href"] == blog_href]
            self.assertEqual(len(blog_links), 1)
            self.assertNotIn("hidden", blog_links[0])
        published = self.snapshot()
        publish(self.root)
        self.assertEqual(self.snapshot(), published)

        source.unlink()
        publish(self.root)
        self.assertFalse((self.root / "blog/first/index.html").exists())
        self.assertEqual(self.snapshot(), empty)
        publish(self.root)
        self.assertEqual(self.snapshot(), empty)

    def test_publishing_preserves_homepage_regions_and_header_targets(self):
        self.post("note")
        publish(self.root)
        home = self.read("index.html")
        self.assertEqual(home.partition(PREVIEW_START)[0], HOMEPAGE.partition(PREVIEW_START)[0])
        self.assertEqual(home.partition(PREVIEW_END)[2], HOMEPAGE.partition(PREVIEW_END)[2])
        for path, prefix in (("blog/index.html", "../"), ("blog/note/index.html", "../../")):
            with self.subTest(path=path):
                header = re.search(r'<header class="site-header">.*?</header>',
                                   self.read(path), re.DOTALL)[0]
                links = Links(header).links
                hrefs = [link["href"] for link in links]
                self.assertEqual(
                    [href for href in hrefs if "#" in href],
                    [f"{prefix}index.html#{section}"
                     for section in ("top", "projects", "personal", "contact", "contact")],
                )
                self.assertEqual(
                    [link for link in links if "data-contact" in link],
                    [{"href": f"{prefix}index.html#contact", "data-contact": contact}
                     for contact in ("github", "email")],
                )

    def test_listing_orders_all_posts_and_homepage_limits_to_latest_three(self):
        for slug, published in (("older", "2025-06-01"), ("beta", "2026-10-18"),
                                ("alpha", "2026-10-18"), ("future", "2099-01-01")):
            self.post(slug, date=published)
        publish(self.root)
        listing = self.read("blog/index.html")
        home = self.read("index.html")
        self.assertEqual([link["href"] for link in self.post_links(listing)],
                         ["future/", "alpha/", "beta/", "older/"])
        self.assertEqual([link["href"] for link in self.post_links(home)],
                         ["blog/future/", "blog/alpha/", "blog/beta/"])
        self.assertEqual(re.findall(r'<h2\b[^>]*>(.*?)</h2>', listing),
                         ["Future", "Alpha", "Beta", "Older"])
        self.assertEqual(re.findall(r'<h3\b[^>]*>(.*?)</h3>', home),
                         ["Future", "Alpha", "Beta"])
        self.assertNotIn('href="blog/older/"', home)
        for slug in ("older", "beta", "alpha", "future"):
            self.assertTrue((self.root / "blog" / slug / "index.html").is_file())

    def test_metadata_is_escaped_and_article_body_and_relative_links_are_unchanged(self):
        body = ('\n<h2>Why</h2>\n<pre><code>if value &lt; 2:\n'
                '    return "ok"\n</code></pre>\n'
                '<p><a href="../other/">Other post</a>'
                '<img src="../../assets/blog/diagram.svg" alt="Diagram"></p>\n')
        self.post("escaping", body=body, title='A < B & "quotes"',
                  summary='Use <tags> & "attributes".', tags=['HTML & <code>', '"Python"'])
        publish(self.root)
        article = self.read("blog/escaping/index.html")
        listing = self.read("blog/index.html")
        home = self.read("index.html")
        self.assertIn(body, article)
        for page in (article, listing, home):
            self.assertIn('A &lt; B &amp; &quot;quotes&quot;', page)
            self.assertIn('Use &lt;tags&gt; &amp; &quot;attributes&quot;.', page)
            self.assertIn('<li>HTML &amp; &lt;code&gt;</li>', page)
            self.assertIn('<li>&quot;Python&quot;</li>', page)
            self.assertIn('<time datetime="2026-10-18">October 18, 2026</time>', page)
        self.assertIn('<meta name="description" content="Use &lt;tags&gt; &amp; &quot;attributes&quot;."', article)
        self.assertIn('href="../../styles.css"', article)
        self.assertIn('href="../../resume/"', article)
        self.assertIn('<a href="../">Blog</a>', article)
        self.assertNotIn('aria-current="page"', article)
        for page in (listing, home):
            self.assertEqual(self.post_links(page)[0]["aria-label"], 'Read post: A < B & "quotes"')
        self.assertIn('href="escaping/"', listing)
        self.assertIn('href="blog/escaping/"', home)

    def test_invalid_sources_fail_with_filename_without_changing_outputs(self):
        self.post("existing")
        publish(self.root)
        self.post("new-valid")
        invalid_metadata = [
            ({key: value for key, value in self.metadata.items() if key != "title"}, "title"),
            (dict(self.metadata, title="  "), "title"),
            (dict(self.metadata, summary=42), "summary"),
            (dict(self.metadata, date="20261018"), "date"),
            (dict(self.metadata, date="2026-1-01"), "date"),
            (dict(self.metadata, date="2026-02-30"), "date"),
            (dict(self.metadata, date=None), "date"),
            (dict(self.metadata, tags=[]), "tags"),
            (dict(self.metadata, tags="Python"), "tags"),
            (dict(self.metadata, tags=[" "]), "tags"),
            (dict(self.metadata, tags=[12]), "tags"),
            ([], "object"),
        ]
        cases = [("zz-invalid", "<!--" + json.dumps(metadata) + "-->" + BODY, detail)
                 for metadata, detail in invalid_metadata]
        cases.extend([
            ("zz-invalid", '<!--{"title": -->' + BODY, "JSON"),
            ("zz-invalid", BODY, "comment"),
            ("zz-invalid", "<!--" + json.dumps(self.metadata) + "--> \n", "body"),
            ("index", "<!--" + json.dumps(self.metadata) + "-->" + BODY, "slug"),
            ("Upper_case", "<!--" + json.dumps(self.metadata) + "-->" + BODY, "slug"),
            ("double--hyphen", "<!--" + json.dumps(self.metadata) + "-->" + BODY, "slug"),
        ])
        for slug, source, detail in cases:
            with self.subTest(slug=slug, detail=detail, source=source):
                path = self.root / "posts" / f"{slug}.html"
                path.write_text(source, encoding="utf-8")
                before = self.snapshot()
                with self.assertRaisesRegex(ValueError, rf"posts/{re.escape(slug)}\.html:.*{detail}"):
                    publish(self.root)
                self.assertEqual(self.snapshot(), before)
                path.unlink()

    def test_removed_posts_prune_only_generated_articles_and_keep_other_files(self):
        self.post("keep")
        gone = self.post("gone")
        assets_source = self.post("with-assets")
        publish(self.root)
        asset = self.root / "blog/with-assets/diagram.svg"
        asset.write_text("<svg></svg>", encoding="utf-8")
        manual = self.root / "blog/manual/index.html"
        manual.parent.mkdir()
        manual.write_text("<h1>Handwritten page</h1>", encoding="utf-8")
        unrelated = self.root / "blog/notes.txt"
        unrelated.write_text("Keep this too.", encoding="utf-8")
        gone.unlink()
        assets_source.unlink()
        publish(self.root)
        self.assertFalse((self.root / "blog/gone").exists())
        self.assertFalse((self.root / "blog/with-assets/index.html").exists())
        self.assertEqual(asset.read_text(encoding="utf-8"), "<svg></svg>")
        self.assertEqual(manual.read_text(encoding="utf-8"), "<h1>Handwritten page</h1>")
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "Keep this too.")
        self.assertTrue((self.root / "blog/keep/index.html").is_file())
        self.assertNotIn('href="gone/"', self.read("blog/index.html"))
        self.assertNotIn('href="blog/with-assets/"', self.read("index.html"))

    def test_output_collision_never_overwrites_a_handwritten_page(self):
        self.post("manual")
        manual = self.root / "blog/manual/index.html"
        manual.parent.mkdir(parents=True)
        manual.write_text("<h1>Handwritten page</h1>", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "blog/manual/index.html: refusing to replace"):
            publish(self.root)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
