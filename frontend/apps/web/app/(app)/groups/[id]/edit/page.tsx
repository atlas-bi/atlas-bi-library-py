import { GroupForm } from '@/components/groups/group-form'
import { getGroup } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { notFound } from 'next/navigation'

export default async function EditGroupPage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const session = await getServerSession(authOptions)
  const groupId = Number(id)

  try {
    const group = await getGroup(session, groupId)
    return <GroupForm initial={group} />
  } catch (error) {
    notFound()
  }
}
