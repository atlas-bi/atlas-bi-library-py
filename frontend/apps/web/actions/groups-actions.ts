'use server'

import { type AtlasGroup, createGroup, updateGroup } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

export type GroupUpsertInput = {
  groupId?: number
  name: string
  account_name: string
  email: string
  group_type: string
}

export async function upsertGroupAction(
  data: GroupUpsertInput
): Promise<AtlasGroup> {
  const session = await getServerSession(authOptions)
  if (!session) {
    throw new Error('Unauthorized')
  }

  let result: AtlasGroup

  if (data.groupId) {
    result = await updateGroup(session, data.groupId, {
      name: data.name,
      account_name: data.account_name,
      email: data.email,
      group_type: data.group_type
    })
  } else {
    result = await createGroup(session, {
      name: data.name,
      account_name: data.account_name,
      email: data.email,
      group_type: data.group_type
    })
  }

  revalidatePath('/groups')
  revalidatePath(`/groups/${result.group_id}`)

  redirect(`/groups/${result.group_id}`)
}
