import { getCollection } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import Link from 'next/link'

export default async function CollectionDetailsPage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const collectionId = Number(id)
  const session = await getServerSession(authOptions)

  const collection = await getCollection(session, collectionId)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-6">
        <div className="w-full">
          <h1 className="text-4xl font-light tracking-tight text-gray-900 mb-6">
            {collection.name}
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
              {collection.reports && collection.reports.length > 0 && (
                <>
                  <li>
                    <span className="text-gray-400 mx-2">/</span>
                  </li>
                  <li>
                    <a
                      href="#reports"
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Linked Reports
                    </a>
                  </li>
                </>
              )}
              {collection.terms && collection.terms.length > 0 && (
                <>
                  <li>
                    <span className="text-gray-400 mx-2">/</span>
                  </li>
                  <li>
                    <a
                      href="#terms"
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Linked Terms
                    </a>
                  </li>
                </>
              )}
            </ul>
          </nav>
        </div>

        <div className="flex flex-col gap-2 flex-shrink-0">
          <Link
            href="/collections"
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Back
          </Link>
          <Link
            href={`/collections/${collection.collection_id}/edit`}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            Edit
          </Link>
        </div>
      </div>

      {collection.initiative && (
        <section className="mb-8">
          <h2
            className="text-3xl font-light text-gray-900 mb-4"
            id="initiative"
          >
            Owning Initiative
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2">
            <div className="rounded border bg-white p-4 shadow-[0_2px_4px_rgba(201,160,80,0.4)]">
              <div className="font-medium text-gray-900">
                {collection.initiative.name}
              </div>
              {collection.initiative.description && (
                <div className="mt-2 text-sm text-gray-600">
                  {collection.initiative.description}
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {collection.reports && collection.reports.length > 0 && (
        <section id="reports" className="mb-8">
          <h2 className="text-3xl font-light text-gray-900 mb-4">Reports</h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {collection.reports
              .slice()
              .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
              .map((r) => (
                <div
                  key={r.link_id}
                  className="flex flex-col rounded bg-white shadow-[0_2px_4px_rgba(201,160,80,0.4)] border border-gray-100 overflow-hidden"
                >
                  <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-white">
                    <div className="font-medium text-gray-900">
                      {r.report.title || r.report.name}
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </section>
      )}

      {collection.terms && collection.terms.length > 0 && (
        <section id="terms" className="mb-8">
          <h2 className="text-3xl font-light text-gray-900 mb-4">Terms</h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {collection.terms
              .slice()
              .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
              .map((t) => (
                <div
                  key={t.link_id}
                  className="flex flex-col rounded bg-white shadow-[0_2px_4px_rgba(201,160,80,0.4)] border border-gray-100 overflow-hidden"
                >
                  <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-white">
                    <div className="font-medium text-gray-900">
                      {t.term.name}
                    </div>
                  </div>
                  {t.term.summary && (
                    <div className="p-4">
                      <div className="text-sm text-gray-600">
                        {t.term.summary}
                      </div>
                    </div>
                  )}
                </div>
              ))}
          </div>
        </section>
      )}

      <section id="details" className="mb-8">
        <h2 className="text-3xl font-light text-gray-900 mb-4">Details</h2>

        <div className="content text-gray-800 max-w-4xl">
          {collection.description && (
            <div className="mb-6">
              <h3 className="text-2xl font-light text-gray-900 mb-3">
                Description
              </h3>
              <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
                {collection.description}
              </div>
            </div>
          )}

          {collection.search_summary && (
            <div className="mb-6">
              <h3 className="text-2xl font-light text-gray-900 mb-3">
                Search Summary
              </h3>
              <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
                {collection.search_summary}
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 max-w-2xl">
          <table className="w-full text-[15px] text-left">
            <tbody className="divide-y divide-gray-100 border-t border-b border-gray-100">
              <tr>
                <td className="py-3 font-medium text-gray-900 w-1/3">
                  Last Updated
                </td>
                <td className="py-3 text-gray-600">
                  {collection.modified_at ?? '-'}
                </td>
              </tr>
              {collection.hidden === 'Y' && (
                <tr>
                  <td className="py-3 font-medium text-gray-900 w-1/3">
                    Hidden from Search?
                  </td>
                  <td className="py-3 text-gray-600">Yes</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
