import { InitiativeForm } from '@/components/initiatives/initiative-form'
import { getInitiative } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { notFound } from 'next/navigation'

export default async function EditInitiativePage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const session = await getServerSession(authOptions)
  const initiativeId = Number(id)

  try {
    const initiative = await getInitiative(session, initiativeId)
    return <InitiativeForm initial={initiative} />
  } catch (error) {
    notFound()
  }
}
