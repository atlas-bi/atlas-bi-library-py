import type { AtlasCollection } from '@/lib/atlas-api'
import Link from 'next/link'

export function CollectionCard({
  collection
}: { collection: AtlasCollection }) {
  const description =
    collection.description?.trim() || collection.search_summary?.trim() || ''

  const excerpt = description
    ? `${description.slice(0, Math.min(160, description.length))}...`
    : ''

  return (
    <div className="rounded-lg border bg-white shadow-sm">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <Link
          href={`/collections/${collection.collection_id}`}
          className="font-semibold text-gray-900 hover:underline"
        >
          {collection.name}
        </Link>
        <span className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-600">
          collection
        </span>
      </div>

      <div className="p-4">
        <div className="flex gap-4">
          <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded bg-gray-100" />
          <div className="flex flex-col justify-between">
            <p className="text-sm text-gray-700">
              {excerpt || (
                <span className="text-purple-600">Open to view details.</span>
              )}
            </p>
            {excerpt ? (
              <Link
                href={`/collections/${collection.collection_id}`}
                className="mt-2 text-sm font-medium text-purple-600 hover:underline"
              >
                read more
              </Link>
            ) : null}
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between border-t px-4 py-3">
        <Link
          href={`/collections/${collection.collection_id}`}
          className="text-sm text-purple-600 hover:underline"
        >
          Open
        </Link>
        <div className="flex gap-3 text-sm text-gray-500">
          <Link
            href={`/collections/${collection.collection_id}/edit`}
            className="hover:underline"
          >
            Edit
          </Link>
        </div>
      </div>
    </div>
  )
}
