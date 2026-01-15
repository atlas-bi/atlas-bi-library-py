import { listCollections } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { CollectionCard } from '@/components/collections/collection-card'
import Link from 'next/link'
import { getServerSession } from 'next-auth'

export default async function CollectionsPage() {
  const session = await getServerSession(authOptions)
  const collections = await listCollections(session)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight text-gray-900">
          Collections
        </h1>
        <Link
          href="/collections/new"
          className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700"
        >
          Create a Collection
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {collections.map((c) => (
          <CollectionCard key={c.collection_id} collection={c} />
        ))}
      </div>
    </div>
  )
}
