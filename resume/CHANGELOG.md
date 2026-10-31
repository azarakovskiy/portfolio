# 31-Oct-2026: Interaction-gated static contacts
- Replaced public Base64 strings and automatic decoding with masked character codes and per-link reveal on browser-trusted interaction.
- Ignored synthetic interaction and print events; native printing still reveals all contacts before rendering the PDF.

# 31-Oct-2026: On-demand PDF through native printing
- Replaced the binary download with a keyboard-accessible Print / Save as PDF button and removed the prepared PDF.
- Restored decoded email and personal-profile links in print; removed the website-only contact block and its visibility rules.
- Changed `?download=true` to open printing after the deferred contact decoder completes, instead of navigating to a PDF file.

# 31-Oct-2026: Contact scraping deterrence
- Encoded the HTML email and personal-profile links through the shared native JavaScript decoder.
- Replaced direct contacts in print mode and the regenerated two-page A4 public PDF with the website contact-section link.

# 31-Oct-2026: Prosus timeline and two-page A4 résumé
- Removed the spoken-languages section and the AI & developer tooling skills group; kept programming languages and frameworks.
- Added Prosus as Senior Software Engineer in Amsterdam, Oct 2026–present, with a company summary, Golang role tag, and the Toqan AI harness work.
- Tightened print-only spacing without reducing font sizes and regenerated `resume_azarakovskiy_senior.pdf` as two A4 pages. Print at 100% scale with browser headers and footers off.
- Moved the main PDF into `resume/` and updated its download link; removed the full-stack résumé HTML and PDF variants.

# 10-Aug-2026: auto-download with ?download=true (resume/index.html)
- Loading the resume with the `download=true` query param programmatically clicks the existing Download PDF link, forcing the PDF download on load.
# 10-Aug-2026: languages presentation (resume/index.html)
- Languages moved out of the header into a one-line `/languages` section after `/education`: proficient are bold, the rest faint
- The freed header contact slot now holds a GitHub link.
