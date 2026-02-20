import { CollectionSnippet } from '@/components/collections/collection-snippet'
import { getReport } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import Link from 'next/link'

export default async function ReportDetailsPage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const reportId = Number(id)
  const session = await getServerSession(authOptions)

  const report = await getReport(session, reportId)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-6">
        <div className="w-full">
          <h1 className="text-4xl font-light tracking-tight text-gray-900 mb-6">
            {report.title || report.name}
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
              {report.collections && report.collections.length > 0 && (
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
            href="/reports"
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors text-center"
          >
            Back
          </Link>
          <Link
            href={`/reports/${report.report_id}/edit`}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors text-center"
          >
            Edit
          </Link>
        </div>
      </div>

      <section id="details" className="mb-8">
        <h2 className="text-3xl font-light text-gray-900 mb-4">Details</h2>

        <div className="content text-gray-800 max-w-4xl">
          {report.description && (
            <div className="mb-6">
              <h3 className="text-2xl font-light text-gray-900 mb-3">
                Description
              </h3>
              <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
                {report.description}
              </div>
            </div>
          )}

          {report.detailed_description && (
            <div className="mb-6">
              <h3 className="text-2xl font-light text-gray-900 mb-3">
                Detailed Description
              </h3>
              <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
                {report.detailed_description}
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 max-w-2xl">
          <table className="w-full text-[15px] text-left">
            <tbody className="divide-y divide-gray-100 border-t border-b border-gray-100">
              <tr>
                <td className="py-3 font-medium text-gray-900 w-1/3">
                  System Server
                </td>
                <td className="py-3 text-gray-600">
                  {report.system_server ?? '-'}
                </td>
              </tr>
              <tr>
                <td className="py-3 font-medium text-gray-900 w-1/3">
                  System DB
                </td>
                <td className="py-3 text-gray-600">
                  {report.system_db ?? '-'}
                </td>
              </tr>
              <tr>
                <td className="py-3 font-medium text-gray-900 w-1/3">
                  System Table
                </td>
                <td className="py-3 text-gray-600">
                  {report.system_table ?? '-'}
                </td>
              </tr>
              {report.system_run_url && (
                <tr>
                  <td className="py-3 font-medium text-gray-900 w-1/3">
                    Run URL
                  </td>
                  <td className="py-3 text-gray-600">
                    <a
                      href={report.system_run_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {report.system_run_url}
                    </a>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {report.collections && report.collections.length > 0 && (
        <section id="collections" className="mb-8">
          <h2 className="text-3xl font-light text-gray-900 mb-4">
            Linked Collections
          </h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {report.collections.map((c) => (
              <CollectionSnippet key={c.collection_id} collection={c} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
