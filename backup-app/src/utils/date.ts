export function isNewYearPeriod(): boolean {
  const now = new Date();
  const month = now.getMonth();
  const day = now.getDate();

  return (month === 11 && day >= 15) || (month === 0 && day <= 13);
}