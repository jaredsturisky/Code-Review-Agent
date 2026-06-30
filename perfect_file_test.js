function formatCurrency(amountInCents, currencyCode = 'USD') {
  if (!Number.isInteger(amountInCents)) {
    throw new TypeError('amountInCents must be an integer.');
  }

  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currencyCode,
  });

  return formatter.format(amountInCents / 100);
}

module.exports = { formatCurrency };
