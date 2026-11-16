const numberFormat = new Intl.NumberFormat('es-AR', {
  maximumFractionDigits: 1,
})

export default function formatNumber(value) {
  return numberFormat.format(value)
}
