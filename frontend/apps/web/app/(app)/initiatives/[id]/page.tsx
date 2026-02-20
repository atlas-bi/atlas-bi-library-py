import { CollectionSnippet } from '@/components/collections/collection-snippet'
import { getInitiative } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import Link from 'next/link'

export default async function InitiativeDetailsPage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const initiativeId = Number(id)
  const session = await getServerSession(authOptions)

  const initiative = await getInitiative(session, initiativeId)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-6">
        <div className="w-full">
          <h1 className="text-4xl font-light tracking-tight text-gray-900 mb-6">
            {initiative.name}
          </h1>

          <nav className="breadcrumb text-sm mb-6">
            <ul className="flex items-center space-x-2">
              <li>
                <a
                  href="#details"
                  className="text-blue-600 hover:text-blue-800"
                >
                  Details
                </a>
              </li>
              {initiative.collections && initiative.collections.length > 0 && (
                <>
                  <li>
                    <span className="text-gray-400 mx-2">/</span>
                  </li>
                  <li>
                    <a
                      href="#collections"
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Linked Collections
                    </a>
                  </li>
                </>
              )}
            </ul>
          </nav>
        </div>

        <div className="flex flex-col gap-2 flex-shrink-0">
          <Link
            href="/initiatives"
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors text-center"
          >
            Back
          </Link>
          <Link
            href={`/initiatives/${initiative.initiative_id}/edit`}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors text-center"
          >
            Edit
          </Link>
        </div>
      </div>

      <section id="details" className="mb-8">
        <h2 className="text-3xl font-light text-gray-900 mb-4">Details</h2>

        <div className="content text-gray-800 max-w-4xl">
          {initiative.description && (
            <div className="mb-6">
              <h3 className="text-2xl font-light text-gray-900 mb-3">
                Description
              </h3>
              <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
                {initiative.description}
              </div>
            </div>
          )}
        </div>
      </section>

      {initiative.collections && initiative.collections.length > 0 && (
        <section id="collections" className="mb-8">
          <h2 className="text-3xl font-light text-gray-900 mb-4">
            Linked Collections
          </h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {initiative.collections.map((c) => (
              <CollectionSnippet key={c.collection_id} collection={c} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
