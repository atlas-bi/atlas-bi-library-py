import { CollectionSnippet } from '@/components/collections/collection-snippet'
import { getTerm } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import Link from 'next/link'

export default async function TermDetailsPage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const termId = Number(id)
  const session = await getServerSession(authOptions)

  const term = await getTerm(session, termId)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-6">
        <div className="w-full">
          <h1 className="text-4xl font-light tracking-tight text-gray-900 mb-6">
            {term.name}
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
              {term.collections && term.collections.length > 0 && (
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
            href="/terms"
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors text-center"
          >
            Back
          </Link>
          <Link
            href={`/terms/${term.term_id}/edit`}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors text-center"
          >
            Edit
          </Link>
        </div>
      </div>

      <section id="details" className="mb-8">
        <h2 className="text-3xl font-light text-gray-900 mb-4">Details</h2>

        <div className="content text-gray-800 max-w-4xl">
          {term.summary && (
            <div className="mb-6">
              <h3 className="text-2xl font-light text-gray-900 mb-3">
                Summary
              </h3>
              <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
                {term.summary}
              </div>
            </div>
          )}

          {term.technical_definition && (
            <div className="mb-6">
              <h3 className="text-2xl font-light text-gray-900 mb-3">
                Technical Definition
              </h3>
              <div className="whitespace-pre-wrap text-[15px] leading-relaxed font-mono">
                {term.technical_definition}
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 max-w-2xl">
          <table className="w-full text-[15px] text-left">
            <tbody className="divide-y divide-gray-100 border-t border-b border-gray-100">
              <tr>
                <td className="py-3 font-medium text-gray-900 w-1/3">
                  Approved?
                </td>
                <td className="py-3 text-gray-600">
                  {term.approved_yn === 'Y' ? 'Yes' : 'No'}
                </td>
              </tr>
              {(term.valid_from || term.valid_to) && (
                <tr>
                  <td className="py-3 font-medium text-gray-900 w-1/3">
                    Validity Period
                  </td>
                  <td className="py-3 text-gray-600">
                    {term.valid_from
                      ? new Date(term.valid_from).toLocaleDateString()
                      : 'N/A'}{' '}
                    to{' '}
                    {term.valid_to
                      ? new Date(term.valid_to).toLocaleDateString()
                      : 'N/A'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {term.collections && term.collections.length > 0 && (
        <section id="collections" className="mb-8">
          <h2 className="text-3xl font-light text-gray-900 mb-4">
            Linked Collections
          </h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {term.collections.map((c) => (
              <CollectionSnippet key={c.collection_id} collection={c} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
