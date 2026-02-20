import { ReportForm } from '@/components/reports/report-form'
import { getReport } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { notFound } from 'next/navigation'

export default async function EditReportPage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const session = await getServerSession(authOptions)
  const reportId = Number(id)

  try {
    const report = await getReport(session, reportId)
    return <ReportForm initial={report} />
  } catch (error) {
    notFound()
  }
}
