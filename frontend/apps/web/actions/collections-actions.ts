'use server'

import {
  createCollection,
  setCollectionLinks,
  updateCollection
} from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { redirect } from 'next/navigation'

export type CollectionUpsertInput = {
  collectionId?: number
  name: string
  search_summary: string
  description: string
  hidden: boolean
  reportIds: number[]
  termIds: number[]
}

export async function upsertCollectionAction(data: CollectionUpsertInput) {
  const session = await getServerSession(authOptions)

  if (session === null) {
    return redirect('/')
  }

  const hidden = data.hidden ? 'Y' : ''

  if (data.collectionId == null) {
    const created = await createCollection(session, {
      name: data.name,
      search_summary: data.search_summary,
      description: data.description,
      hidden
    })

    await setCollectionLinks(session, created.collection_id, {
      report_ids: data.reportIds,
      term_ids: data.termIds
    })

    return redirect(`/collections/${created.collection_id}`)
  }

  await updateCollection(session, data.collectionId, {
    name: data.name,
    search_summary: data.search_summary,
    description: data.description,
    hidden
  })

  await setCollectionLinks(session, data.collectionId, {
    report_ids: data.reportIds,
    term_ids: data.termIds
  })

  return redirect(`/collections/${data.collectionId}`)
}
