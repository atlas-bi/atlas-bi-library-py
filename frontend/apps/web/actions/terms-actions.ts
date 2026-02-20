'use server'

import { type AtlasTerm, createTerm, updateTerm } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

export type TermUpsertInput = {
  termId?: number
  name: string
  summary: string
  technical_definition?: string
}

export async function upsertTermAction(
  data: TermUpsertInput
): Promise<AtlasTerm> {
  const session = await getServerSession(authOptions)
  if (!session) {
    throw new Error('Unauthorized')
  }

  let result: AtlasTerm

  if (data.termId) {
    result = await updateTerm(session, data.termId, {
      name: data.name,
      summary: data.summary,
      technical_definition: data.technical_definition
    })
  } else {
    result = await createTerm(session, {
      name: data.name,
      summary: data.summary,
      technical_definition: data.technical_definition
    })
  }

  revalidatePath('/terms')
  revalidatePath(`/terms/${result.term_id}`)

  redirect(`/terms/${result.term_id}`)
}
