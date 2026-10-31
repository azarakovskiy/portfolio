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
