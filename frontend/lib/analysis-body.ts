/** Normalize LLM `Body` into paragraphs (array or blank-line-separated string). */
export function normalizeBodyParagraphs(body: string | string[] | undefined): string[] {
  if (body === undefined) return [];
  if (Array.isArray(body)) return body.map((p) => p.trim()).filter(Boolean);
  return body
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);
}

/** Teaser for the first paragraph when more copy follows (word boundary when possible). */
export function truncateIntro(text: string, maxChars: number): string {
  const t = text.trim();
  if (!t || t.length <= maxChars) return t;
  const slice = t.slice(0, maxChars);
  const lastSpace = slice.lastIndexOf(" ");
  return (lastSpace > maxChars * 0.5 ? slice.slice(0, lastSpace) : slice).trim();
}
