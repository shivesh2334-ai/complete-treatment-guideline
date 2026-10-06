# Complete Treatment Guideline

A static clinician reference application with disease-wise ICMR/DHR and Ministry of Health & Family Welfare sources. Search conditions, filter specialties and source coverage, open an official PDF or read it in the application, and inspect separately identified historical Gujarat 2013 text.

## What this update contains

- All **289 original entries** retained, with corrected specialty assignment, stable IDs, source references and explicit clinical review status.
- **10 missing topics** added: heart failure, NSTEMI, STEMI, COPD, respiratory failure, community acquired pneumonia, hospital acquired pneumonia, generalized anxiety disorder, OCD and gastrointestinal bleeding.
- **149 official source records**, with publisher, known edition, catalogue URL and checking date.
- **104 entries** with a condition source or disease heading located, **17** with a related workflow, and **178** with specialty references only. A disease heading match confirms a location, not current clinical validation.
- **Three source-specific clinical summaries**: hypertension (MoHFW 2016), adult type 2 diabetes (ICMR 2022), and scabies (ICMR 2022). Only hypertension and scabies include source-supported regimen details. Missing doses and durations are explicitly left unspecified.
- Hypertension summary uses the source's amlodipine maximum **10 mg once daily**, rather than the erroneous/unreviewed higher range in the historical extraction. PDF page 132 supports that regimen.
- Historical text is loaded only when its expandable archive is opened. The former isolated drug-line quick list was removed because alternatives, populations and adjacent-condition text can be lost in automatic extraction.

## Clinical scope and limitations

**This update does not revalidate the treatment of every disease.** The status of source coverage and the status of clinical regimen review are separate fields. `sourceStatus: condition-source` is not equivalent to `regimenStatus: source-summary`.

Several ICMR full-PDF fetches failed during this work. Official catalogue-listed links are included, but their contents are not claimed as reviewed. Date fields are null when the edition cannot be confirmed. A 2026 upload filename is not evidence of a 2026 guideline edition. MoHFW hosts both dated and undated documents, including explicitly labelled drafts; listing on the portal does not establish that a document is the latest recommendation.

The source summaries reflect the named edition, not a claim of latest practice in 2026. They still require clinician review. Adult and pediatric content are not transferred between populations. Emergency care, renal/hepatic adjustments, interactions and other special populations must be checked in the full disease-specific guideline and prescribing reference.

The retained 2013 archive is an unreviewed automatic transcription. Some original sections include adjacent diseases and table alignment can be lost. The archive is historical, not revised treatment. No patient data, keys, database or AI service is required.

## Official resources

- [ICMR Standard Treatment Workflows](https://www.icmr.gov.in/standard-treatment-workflows-stws)
- [ICMR downloadable books: Volumes 1–3](https://www.icmr.gov.in/downloadable-books)
- [MoHFW specialty and national-programme guidelines](https://clinicalestablishments.mohfw.gov.in/en/standard-treatment-guidelines)

Checked **6 October 2026**. PDFs are linked on the official websites rather than reproduced. Source PDFs may block in-page embedding; the direct link is always available.

## Development and deployment

```
npm test
npm start
```

Open http://localhost:3001. This is static HTML/CSS/JavaScript; no installation or build is required. On Vercel use framework **Other**, leave build/install commands empty, and use the repository root as the output. `vercel.json` preserves static JSON/assets and includes security headers. `/guidelines/*` routes resolve to the app. The old HTML filename redirects to the current app.

The tests check catalogue completeness, source integrity, population boundaries, regimen provenance, coverage counts and static asset routing. Browser testing was unavailable in this environment because the browser binary download failed; source PDFs' external rendering also depends on browser support.

## Data model and maintenance

- `data/conditions.json`: stable IDs, specialty, population, references, source/clinical statuses and reviewed source summaries.
- `data/sources.json`: official source metadata and full-document retrieval status.
- `data/coverage.json`: coverage and limitations.
- `data/legacy.json`: preserved original 2013 transcription.
- `scripts/build-catalogue.py`: explicit disease/workflow routing and optional disease-heading matching against downloaded MoHFW PDFs. Requires PyMuPDF for optional page matching. A page match never synthesizes a regimen.

Before adding a clinical summary, read the actual source, confirm its population and edition, record source page when possible, and independently check every dose, route, duration, contraindication and treatment alternative. Set regimen status only for the summary that was actually checked. Do not promote a reference-only entry to clinically updated.
