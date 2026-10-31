# Portfolio

A static portfolio and blog built with HTML and CSS. The portfolio is served
directly from the root `index.html` (`/`), without a redirect. The résumé stays
in `resume/`, and the blog lives at `/blog/`.

The blog publisher uses only the Python standard library and requires Python 3.9
or newer. Generated pages are committed, so the deployed site needs neither
Python nor a build service.

## Portfolio layout

Keep employer and project entries in their current timeline order, with matching
horizontal rules between employers. Use the sections specified in the approved
draft. Prose fills its content column and
uses native `text-wrap: pretty` to reduce single-word last lines. Headings use
`balance` where needed. The AI tools group spans the full stack-grid width.

Copy edits must preserve facts in the approved draft, including figures, their
qualifiers, team ownership, technical decisions, and named clients. Apply its
merge and removal instructions without reintroducing older content.
Omit leading "a" and "an" from titles and short subtitles; keep body prose grammatical.

## Blog layout

The selected B design gives the newest post a mint feature panel and places
supporting posts in two columns with shared content tracks. Titles are plain
headings with separate, right-aligned "Read post" links. Article pages use a
full-width mint title band above a centered, narrow reading column. The layout
collapses to one column on smaller screens and uses native HTML and CSS without
blog JavaScript or sample content.

The final prototype is archived on branch
`prototype/blog-featured-final-f3c5c1ba` at commit `1b2242363c694788562def185f3aff9d6327a1cc`.

## Write a post

Create `posts/<slug>.html`. Use lowercase letters and numbers separated by single
hyphens, for example `notes-on-static-publishing`. The slug `index` is reserved.
Only `.html` files directly inside `posts/` are published.

Start the file with an HTML comment containing a JSON object, then write the
article as an HTML fragment. This example is illustrative documentation, not a
published article:

```html
<!--
{
  "title": "Illustrative post title (replace before publishing)",
  "date": "2026-10-18",
  "tags": ["Python", "Static sites"],
  "summary": "Replace this sentence with a short, factual description of the article."
}
-->
<p>Write the article introduction here.</p>
<h2>A descriptive section heading</h2>
<p>Use semantic HTML for the article body.</p>
<pre tabindex="0" aria-label="Python example"><code class="language-python">if value &lt; 2:
    print("Escape &lt;, &gt;, and &amp; in code examples.")
</code></pre>
```

All four metadata fields are required. `title` and `summary` must be nonblank
strings. `date` must be a real calendar date in `YYYY-MM-DD` form. `tags` must
contain at least one nonblank string. The body must not be blank.

The publisher supplies the article's `h1`, date, tags, and summary. Start body
sections at `h2`, then use `h3` for subsections. Use paragraphs, lists,
blockquotes, figures with descriptive image alternatives, and links as
appropriate. Escape literal `<`, `>`, and `&` inside code examples as `&lt;`,
`&gt;`, and `&amp;`. The publisher escapes metadata but deliberately copies body
HTML unchanged. Write trusted repository-authored HTML; it does not sanitize
content or parse Markdown.
Give wide code blocks `tabindex="0"` and a descriptive `aria-label` so keyboard
readers can focus and scroll them.

Wrap wide tables in a labelled, keyboard-focusable scrolling region:

```html
<div class="table-scroll" tabindex="0" role="region" aria-label="Example comparison">
  <table>
    <caption>Example comparison</caption>
    <thead><tr><th scope="col">Approach</th><th scope="col">Trade-off</th></tr></thead>
    <tbody><tr><th scope="row">Static HTML</th><td>Regenerate after edits</td></tr></tbody>
  </table>
</div>
```

Asset links resolve from the generated article URL, not from `posts/`. For an
image committed at `assets/blog/<slug>/diagram.svg`, use
`src="../../assets/blog/<slug>/diagram.svg"` in the article. Link to another
article with `href="../other-slug/"`. The publisher does not copy assets or
rewrite body links.

Keep unpublished drafts outside `posts/`. Dates control display and ordering,
not scheduling: a future-dated source is published as soon as the publisher
runs. With no sources, the portfolio has no blog preview and the Blog navigation
link is hidden across the site. The direct `/blog/` URL still shows an empty
listing. Publishing the first source restores the preview and link; deleting
the last source and republishing hides them again.

## Publish and preview

Run from the repository root:

```sh
python3 scripts/publish_blog.py
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m http.server 4187 --bind 127.0.0.1
```

The publisher creates `blog/index.html` and `blog/<slug>/index.html`, updates
the region between `blog-preview:start` and `blog-preview:end` in the root
`index.html`, and sets or removes `hidden` on the header's Blog link.
Keep the preview markers and the `href="blog/"` header anchor intact.
The listing shows every post, newest date first, with ascending slug order for
matching dates. The portfolio shows the latest three. Each article has a
permanent URL at `blog/<slug>/`. The publisher never reads or writes `resume/`.

Validation errors name the source file and the invalid field or content, then
exit with a nonzero status before changing output. Fix the source and rerun.
The publisher also refuses to overwrite a blog output file that lacks its
generated-file marker.

Preview these pages after generation:

- Portfolio: <http://127.0.0.1:4187/> opens directly, without a redirect.
- Résumé and PDF download links: <http://127.0.0.1:4187/resume/index.html>
- Listing: <http://127.0.0.1:4187/blog/>
- Each article directly: `http://127.0.0.1:4187/blog/<slug>/`

Résumé links use the explicit `resume/index.html` file so they also work when
opening the portfolio directly from disk, without a web server.

Check desktop and mobile layouts, including 390px and 320px widths. Check title
and tag wrapping, code and table scrolling, image sizing, metadata, and all
links. Navigate with the keyboard to check focus, the skip link, and scrollable
tables. Reload an article's direct URL rather than relying only on navigation
from the listing. With no sources, check that the portfolio has no blog section
and the Blog link is hidden on both the portfolio and listing. Check that the
first published source restores the preview and navigation, and removing the
last source hides them again. Confirm that the root opens the portfolio directly
and that the résumé and its PDF download links work.

After editing or deleting a source, rerun the publisher and repeat the checks.
Keep a published filename stable: renaming it changes its URL and does not
create a redirect. Removing a source removes only its marked generated
`index.html`; the publisher removes its directory only when empty and leaves
assets and unrelated files alone.

Do not edit generated blog HTML or the generated portfolio preview by hand.
Edit article sources instead. The publisher reads the shared site header from
the root `index.html`, so rerun it after changing header navigation. It manages
the Blog link's visibility; other portfolio content and `resume/` are outside
its output.

Commit the sources, publisher and tests, documentation, any article assets,
updated root `index.html`, and generated `blog/` output together.
Hosting-specific deployment commands are not documented here.
Deploy the committed files through the existing static host's normal process;
the host only needs to serve static files and directory `index.html` pages.
It does not run the publisher.
