import { getCollection } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import Link from 'next/link'
import { getServerSession } from 'next-auth'

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
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-gray-900">
            {collection.name}
          </h1>

          <nav className="mt-2 flex gap-3 text-sm text-gray-600">
            <a href="#details" className="hover:underline">
              Details
            </a>
            {collection.reports && collection.reports.length > 0 ? (
              <a href="#reports" className="hover:underline">
                Linked Reports
              </a>
            ) : null}
            {collection.terms && collection.terms.length > 0 ? (
              <a href="#terms" className="hover:underline">
                Linked Terms
              </a>
            ) : null}
          </nav>
        </div>

        <div className="flex flex-col gap-2">
          <Link
            href="/collections"
            className="rounded-md border bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Back
          </Link>
          <Link
            href={`/collections/${collection.collection_id}/edit`}
            className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700"
          >
            Edit
          </Link>
        </div>
      </div>

      {collection.initiative ? (
        <section>
          <h2 className="text-lg font-semibold text-gray-900">Owning Initiative</h2>
          <div className="mt-3 rounded-lg border bg-white p-4">
            <div className="font-medium text-gray-900">
              {collection.initiative.name}
            </div>
            {collection.initiative.description ? (
              <div className="mt-1 text-sm text-gray-600">
                {collection.initiative.description}
              </div>
            ) : null}
          </div>
        </section>
      ) : null}

      {collection.reports && collection.reports.length > 0 ? (
        <section id="reports">
          <h2 className="text-lg font-semibold text-gray-900">Reports</h2>
          <div className="mt-3 grid grid-cols-1 gap-4 md:grid-cols-2">
            {collection.reports
              .slice()
              .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
              .map((r) => (
                <div
                  key={r.link_id}
                  className="rounded-lg border bg-white p-4"
                >
                  <div className="font-medium text-gray-900">
                    {r.report.title || r.report.name}
                  </div>
                </div>
              ))}
          </div>
        </section>
      ) : null}

      {collection.terms && collection.terms.length > 0 ? (
        <section id="terms">
          <h2 className="text-lg font-semibold text-gray-900">Terms</h2>
          <div className="mt-3 grid grid-cols-1 gap-4 md:grid-cols-2">
            {collection.terms
              .slice()
              .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
              .map((t) => (
                <div
                  key={t.link_id}
                  className="rounded-lg border bg-white p-4"
                >
                  <div className="font-medium text-gray-900">{t.term.name}</div>
                  {t.term.summary ? (
                    <div className="mt-1 text-sm text-gray-600">
                      {t.term.summary}
                    </div>
                  ) : null}
                </div>
              ))}
          </div>
        </section>
      ) : null}

      <section id="details">
        <h2 className="text-lg font-semibold text-gray-900">Details</h2>

        {collection.description ? (
          <div className="mt-3 rounded-lg border bg-white p-4">
            <h3 className="font-medium text-gray-900">Description</h3>
            <div className="mt-2 whitespace-pre-wrap text-sm text-gray-700">
              {collection.description}
            </div>
          </div>
        ) : null}

        {collection.search_summary ? (
          <div className="mt-4 rounded-lg border bg-white p-4">
            <h3 className="font-medium text-gray-900">Search Summary</h3>
            <div className="mt-2 whitespace-pre-wrap text-sm text-gray-700">
              {collection.search_summary}
            </div>
          </div>
        ) : null}

        <div className="mt-4 overflow-hidden rounded-lg border bg-white">
          <table className="w-full text-sm">
            <tbody>
              <tr className="border-b">
                <td className="w-48 bg-gray-50 px-4 py-3 font-medium text-gray-700">
                  Last Updated
                </td>
                <td className="px-4 py-3 text-gray-700">
                  {collection.modified_at ?? '-'}
                </td>
              </tr>
              <tr>
                <td className="w-48 bg-gray-50 px-4 py-3 font-medium text-gray-700">
                  Hidden from Search?
                </td>
                <td className="px-4 py-3 text-gray-700">
                  {collection.hidden === 'Y' ? 'Yes' : 'No'}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
