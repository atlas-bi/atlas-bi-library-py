import { CollectionForm } from '@/components/collections/collection-form'
import { getCollection } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'

export default async function EditCollectionPage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const collectionId = Number(id)

  const session = await getServerSession(authOptions)
  const collection = await getCollection(session, collectionId)

  return <CollectionForm initial={collection} />
}
