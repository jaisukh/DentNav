export function readinessLabel(score: number): string {
  if (score >= 75) return "Strong Candidate";
  if (score >= 60) return "On Track";
  return "Build Momentum";
}
