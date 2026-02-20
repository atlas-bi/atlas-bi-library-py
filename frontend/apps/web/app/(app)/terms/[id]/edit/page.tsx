import { TermForm } from '@/components/terms/term-form'
import { getTerm } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { notFound } from 'next/navigation'

export default async function EditTermPage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const session = await getServerSession(authOptions)
  const termId = Number(id)

  try {
    const term = await getTerm(session, termId)
    return <TermForm initial={term} />
  } catch (error) {
    notFound()
  }
}
