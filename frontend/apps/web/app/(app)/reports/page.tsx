import { listReports } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import Link from 'next/link'

export default async function ReportsPage() {
  const session = await getServerSession(authOptions)
  const reports = await listReports(session)

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-4xl font-light tracking-tight text-gray-900 mb-6">
        Reports
      </h1>

      {session && (
        <div className="mb-6 flex">
          <Link
            href="/reports/new"
            className="inline-flex items-center gap-2 rounded bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 border border-gray-300 transition-colors"
            title="new report"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <title>Create report</title>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Create a Report
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {reports.map((report) => (
          <div
            key={report.report_id}
            className="flex flex-col rounded bg-white shadow-[0_2px_4px_rgba(201,160,80,0.4)] border border-gray-100 overflow-hidden h-full"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-white">
              <Link
                href={`/reports/${report.report_id}`}
                className="font-medium text-gray-900 hover:text-gray-600 flex items-center gap-2"
              >
                {report.title || report.name}
              </Link>
              <span className="rounded bg-gray-100 px-3 py-1 text-[11px] uppercase tracking-wider text-gray-600 font-semibold">
                report
              </span>
            </div>

            <div className="flex p-4 gap-4 flex-grow">
              <div className="flex flex-col flex-grow">
                <Link
                  href={`/reports/${report.report_id}`}
                  className="text-gray-700 hover:text-gray-900 group flex-grow"
                >
                  <p className="text-sm leading-relaxed">
                    {report.description ? (
                      <>
                        {report.description.slice(
                          0,
                          Math.min(160, report.description.length)
                        )}
                        ...
                        <span className="text-blue-600 group-hover:underline ml-1">
                          read more
                        </span>
                      </>
                    ) : (
                      <span className="text-blue-600 group-hover:underline">
                        Open to view details.
                      </span>
                    )}
                  </p>
                </Link>
              </div>
            </div>

            <div className="flex items-center justify-between border-t border-gray-100 bg-gray-50/50">
              <button
                type="button"
                className="flex items-center gap-2 px-4 py-3 text-sm text-gray-600 hover:bg-gray-100 transition-colors border-r border-gray-100 flex-grow justify-center sm:flex-grow-0"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <title>Star</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                  />
                </svg>
                <span>
                  Star{' '}
                  <span className="inline-flex items-center justify-center px-2 py-0.5 ml-1 text-xs font-medium bg-gray-200 text-gray-800 rounded-full">
                    0
                  </span>
                </span>
              </button>

              <div className="flex items-center divide-x divide-gray-100">
                <Link
                  href={`/reports/${report.report_id}`}
                  className="p-3 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                  title="Open Report Profile"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <title>Open</title>
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </Link>
                <button
                  type="button"
                  className="p-3 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                  title="Share"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <title>Share</title>
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
