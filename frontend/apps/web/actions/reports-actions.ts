'use server'

import { type AtlasReport, createReport, updateReport } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

export type ReportUpsertInput = {
  reportId?: number
  title: string
  name: string
  description: string
  detailed_description?: string
}

export async function upsertReportAction(
  data: ReportUpsertInput
): Promise<AtlasReport> {
  const session = await getServerSession(authOptions)
  if (!session) {
    throw new Error('Unauthorized')
  }

  let result: AtlasReport

  if (data.reportId) {
    result = await updateReport(session, data.reportId, {
      title: data.title,
      name: data.name,
      description: data.description,
      detailed_description: data.detailed_description
    })
  } else {
    result = await createReport(session, {
      title: data.title,
      name: data.name,
      description: data.description,
      detailed_description: data.detailed_description
    })
  }

  revalidatePath('/reports')
  revalidatePath(`/reports/${result.report_id}`)

  redirect(`/reports/${result.report_id}`)
}
