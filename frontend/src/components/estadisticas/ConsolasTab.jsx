import { useEffect, useState } from 'react'

import { requestStatistics } from '../../api/estadisticas'
import {
  BarChart,
  ChartCard,
  SectionHeading,
  StatCard,
  StatisticsStatus,
} from './StatisticsComponents'
import formatNumber from '../../utils/formatNumber'

export default function ConsolasTab() {
  const [result, setResult] = useState({ status: 'loading', data: null })

  useEffect(() => {
    const controller = new AbortController()

    async function loadStatistics() {
      try {
        const data = await requestStatistics(
          '/api/estadisticas/consolas',
          controller.signal,
        )
        setResult({ status: 'success', data })
      } catch (error) {
        if (error.name !== 'AbortError') {
          setResult({ status: 'error', data: null, message: error.message })
        }
      }
    }

    loadStatistics()
    return () => controller.abort()
  }, [])

  if (result.status !== 'success') {
    return (
      <StatisticsStatus
        status={result.status}
        message={result.message}
        loadingMessage="Consultando las estadísticas de consolas..."
      />
    )
  }

  const { summary, consoles, salesByManufacturer, salesByGeneration, releasesByDecade } =
    result.data
  const topConsole = consoles[0]

  return (
    <>
      <SectionHeading
        eyebrow="HARDWARE"
        title="Estadísticas de consolas"
        description="Datos de consolas, fabricantes y generaciones."
      />
      <section className="stats-grid" aria-label="Resumen de consolas">
        <StatCard
          label="Consolas registradas"
          value={formatNumber(summary.consoleCount)}
          note="en la base de datos"
        />
        <StatCard
          label="Ventas de hardware"
          value={`${formatNumber(summary.totalSales)} M`}
          note="unidades de consola"
        />
        <StatCard
          label="Fabricantes"
          value={formatNumber(summary.manufacturerCount)}
          note="con consolas registradas"
        />
        <StatCard
          label="Consola más vendida"
          value={topConsole?.name ?? 'Sin datos'}
          note={
            topConsole
              ? `${formatNumber(topConsole.sales)} M de unidades`
              : 'No hay ventas disponibles'
          }
          featured
        />
      </section>

      <section className="charts-grid" aria-label="Gráficos de consolas">
        <ChartCard
          eyebrow="RANKING"
          title="Consolas más vendidas"
          description="Ventas totales registradas, en millones de unidades."
          index="01"
          wide
        >
          <BarChart
            items={consoles.slice(0, 10).map((item) => ({
              name: item.name,
              sales: item.sales,
              detail: 'Ventas totales de hardware',
            }))}
          />
        </ChartCard>

        <ChartCard
          eyebrow="COMPARACIÓN"
          title="Ventas por fabricante"
          description="Suma de ventas de sus consolas."
          index="02"
        >
          <BarChart
            items={salesByManufacturer.map((item) => ({
              name: item.name,
              sales: item.sales,
              consoleCount: item.consoleCount,
            }))}
            color="purple"
          />
        </ChartCard>

        <ChartCard
          eyebrow="COMPARACIÓN"
          title="Ventas por generación"
          description="Suma de unidades de hardware por generación."
          index="03"
        >
          <BarChart
            items={salesByGeneration.map((item) => ({
              name: item.name,
              sales: item.sales,
              consoleCount: item.consoleCount,
            }))}
            color="green"
          />
        </ChartCard>

        <ChartCard
          eyebrow="LANZAMIENTOS"
          title="Consolas lanzadas por década"
          description="Cantidad según año de lanzamiento; no son ventas anuales."
          index="04"
          wide
        >
          <BarChart
            items={releasesByDecade.map((item) => ({
              name: item.decade,
              consoleCount: item.consoleCount,
            }))}
            valueKey="consoleCount"
            unit=""
            color="orange"
          />
        </ChartCard>
      </section>
    </>
  )
}
