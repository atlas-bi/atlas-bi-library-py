'use server'

import {
  type AtlasInitiative,
  createInitiative,
  updateInitiative
} from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

export type InitiativeUpsertInput = {
  initiativeId?: number
  name: string
  description: string
}

export async function upsertInitiativeAction(
  data: InitiativeUpsertInput
): Promise<AtlasInitiative> {
  const session = await getServerSession(authOptions)
  if (!session) {
    throw new Error('Unauthorized')
  }

  let result: AtlasInitiative

  if (data.initiativeId) {
    result = await updateInitiative(session, data.initiativeId, {
      name: data.name,
      description: data.description
    })
  } else {
    result = await createInitiative(session, {
      name: data.name,
      description: data.description
    })
  }

  revalidatePath('/initiatives')
  revalidatePath(`/initiatives/${result.initiative_id}`)

  redirect(`/initiatives/${result.initiative_id}`)
}
