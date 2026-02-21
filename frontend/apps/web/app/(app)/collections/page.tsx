import { CollectionSnippet } from '@/components/collections/collection-snippet'
import { listCollections } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import Link from 'next/link'

export default async function CollectionsPage() {
  const session = await getServerSession(authOptions)
  const collections = await listCollections(session)

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-4xl font-light tracking-tight text-gray-900">
        Collections
      </h1>

      {session && (
        <div className="flex">
          <Link
            href="/collections/new"
            className="inline-flex items-center gap-2 rounded bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 border border-gray-300 transition-colors"
            title="new collection"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <title>Create collection</title>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Create a Collection
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {collections.map((c) => (
          <CollectionSnippet key={c.collection_id} collection={c} />
        ))}
      </div>
    </div>
  )
}
