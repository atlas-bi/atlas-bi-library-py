'use client'

import type { CollectionUpsertInput } from '@/actions/collections-actions'
import { upsertCollectionAction } from '@/actions/collections-actions'
import type {
  AtlasCollection,
  AtlasReportSearchResult,
  AtlasTermSearchResult
} from '@/lib/atlas-api'
import { useSession } from 'next-auth/react'
import Link from 'next/link'
import { useMemo, useState, useTransition } from 'react'

type SelectedReport = { report_id: number; title: string; name: string }
type SelectedTerm = { term_id: number; name: string }

export function CollectionForm({
  initial
}: {
  initial?: AtlasCollection
}) {
  const { data: session } = useSession()
  const [isPending, startTransition] = useTransition()

  const [name, setName] = useState(initial?.name ?? '')
  const [searchSummary, setSearchSummary] = useState(
    initial?.search_summary ?? ''
  )
  const [description, setDescription] = useState(initial?.description ?? '')
  const [hidden, setHidden] = useState(initial?.hidden === 'Y')

  const initialReports = useMemo<SelectedReport[]>(() => {
    return (
      initial?.reports
        ?.slice()
        .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
        .map((x) => ({
          report_id: x.report.report_id,
          title: x.report.title,
          name: x.report.name
        })) ?? []
    )
  }, [initial])

  const initialTerms = useMemo<SelectedTerm[]>(() => {
    return (
      initial?.terms
        ?.slice()
        .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
        .map((x) => ({
          term_id: x.term.term_id,
          name: x.term.name
        })) ?? []
    )
  }, [initial])

  const [selectedReports, setSelectedReports] =
    useState<SelectedReport[]>(initialReports)
  const [selectedTerms, setSelectedTerms] =
    useState<SelectedTerm[]>(initialTerms)

  const [reportQuery, setReportQuery] = useState('')
  const [termQuery, setTermQuery] = useState('')
  const [reportResults, setReportResults] = useState<AtlasReportSearchResult[]>(
    []
  )
  const [termResults, setTermResults] = useState<AtlasTermSearchResult[]>([])

  async function runReportSearch(q: string) {
    if (!session || q.trim().length < 2) {
      setReportResults([])
      return
    }

    const qp = new URLSearchParams({ q: q.trim() })
    const res = await fetch(`/api/atlas/search/reports?${qp.toString()}`)
    if (!res.ok) {
      setReportResults([])
      return
    }
    setReportResults((await res.json()) as AtlasReportSearchResult[])
  }

  async function runTermSearch(q: string) {
    if (!session || q.trim().length < 2) {
      setTermResults([])
      return
    }

    const qp = new URLSearchParams({ q: q.trim() })
    const res = await fetch(`/api/atlas/search/terms?${qp.toString()}`)
    if (!res.ok) {
      setTermResults([])
      return
    }
    setTermResults((await res.json()) as AtlasTermSearchResult[])
  }

  function submit() {
    const payload: CollectionUpsertInput = {
      collectionId: initial?.collection_id,
      name,
      search_summary: searchSummary,
      description,
      hidden,
      reportIds: selectedReports.map((r) => r.report_id),
      termIds: selectedTerms.map((t) => t.term_id)
    }

    startTransition(async () => {
      await upsertCollectionAction(payload)
    })
  }

  return (
    <div className="flex flex-col gap-6 max-w-5xl">
      <h1 className="text-4xl font-light tracking-tight text-gray-900 mb-2">
        {initial ? `Editing ${initial.name}` : 'New Collection'}
      </h1>

      <div className="flex justify-between items-center mb-6">
        <Link
          href={
            initial ? `/collections/${initial.collection_id}` : '/collections'
          }
          className="flex items-center gap-3 px-6 py-4 bg-white border border-gray-200 rounded shadow-sm hover:bg-gray-50 transition-colors group"
        >
          <svg
            className="w-6 h-6 text-gray-400 group-hover:text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <title>Back</title>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 19l-7-7m0 0l7-7m-7 7h18"
            />
          </svg>
          <div className="text-left">
            <div className="font-semibold text-gray-900">Cancel</div>
            <div className="text-sm text-gray-500">Go Back</div>
          </div>
        </Link>

        <button
          type="button"
          onClick={submit}
          disabled={isPending || !session}
          className="flex items-center gap-3 px-6 py-4 bg-white border border-gray-200 rounded shadow-sm hover:bg-gray-50 transition-colors disabled:opacity-50 group"
        >
          <div className="text-right">
            <div className="font-semibold text-gray-900">Save</div>
            <div className="text-sm text-gray-500">and Continue</div>
          </div>
          <svg
            className="w-6 h-6 text-gray-400 group-hover:text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <title>Save</title>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M14 5l7 7m0 0l-7 7m7-7H3"
            />
          </svg>
        </button>
      </div>

      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-2">
          <label
            htmlFor="collection-name"
            className="text-base font-medium text-gray-900"
          >
            Name
          </label>
          <input
            id="collection-name"
            className="w-full rounded border border-gray-300 px-4 py-2.5 shadow-inner focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g Data Sorting"
            required
          />
        </div>

        <div className="flex flex-col gap-2">
          <label
            htmlFor="collection-purpose"
            className="text-base font-medium text-gray-900"
          >
            Purpose
          </label>
          <textarea
            id="collection-purpose"
            className="w-full rounded border border-gray-300 px-4 py-3 shadow-inner focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors font-mono text-sm"
            value={searchSummary}
            onChange={(e) => setSearchSummary(e.target.value)}
            rows={4}
          />
        </div>

        <div className="flex flex-col gap-2">
          <label
            htmlFor="collection-description"
            className="text-base font-medium text-gray-900"
          >
            Description
          </label>
          <textarea
            id="collection-description"
            className="w-full rounded border border-gray-300 px-4 py-3 shadow-inner focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors font-mono text-sm"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={6}
          />
        </div>

        <div className="flex items-center gap-3 py-2">
          <div className="relative inline-block w-12 mr-2 align-middle select-none transition duration-200 ease-in">
            <input
              type="checkbox"
              name="toggle"
              id="hidden"
              checked={hidden}
              onChange={(e) => setHidden(e.target.checked)}
              className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer transition-transform duration-200 ease-in-out"
              style={{
                transform: hidden ? 'translateX(100%)' : 'translateX(0)',
                borderColor: hidden ? '#3b82f6' : '#d1d5db'
              }}
            />
            <label
              htmlFor="hidden"
              className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer transition-colors duration-200 ease-in-out"
              style={{ backgroundColor: hidden ? '#3b82f6' : '#d1d5db' }}
            >
              <span className="sr-only">Toggle hidden</span>
            </label>
          </div>
          <label
            htmlFor="hidden"
            className="text-base text-gray-900 font-medium cursor-pointer"
          >
            Hide Collection?
          </label>
        </div>

        <div className="flex flex-col gap-2 mt-2">
          <div className="text-base font-medium text-gray-900">
            Linked Terms
          </div>
          <div className="flex flex-wrap gap-2 mb-2">
            {selectedTerms.map((t) => (
              <div
                key={t.term_id}
                className="inline-flex items-center bg-blue-100 text-blue-800 rounded px-3 py-1 text-sm font-medium"
              >
                {t.name}
                <button
                  type="button"
                  onClick={() =>
                    setSelectedTerms((prev) =>
                      prev.filter((x) => x.term_id !== t.term_id)
                    )
                  }
                  className="ml-2 text-blue-600 hover:text-blue-900 focus:outline-none"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          <div className="relative">
            <input
              className="w-full rounded border border-gray-300 px-4 py-2.5 shadow-inner focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors"
              placeholder="search for terms.."
              value={termQuery}
              onChange={(e) => {
                const q = e.target.value
                setTermQuery(q)
                void runTermSearch(q)
              }}
            />
            {termResults.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded shadow-lg max-h-60 overflow-y-auto">
                {termResults.map((r) => (
                  <button
                    key={r.term_id}
                    type="button"
                    className="w-full text-left px-4 py-2 hover:bg-blue-50 focus:bg-blue-50 outline-none text-sm text-gray-700"
                    onClick={() => {
                      setSelectedTerms((prev) =>
                        prev.some((x) => x.term_id === r.term_id)
                          ? prev
                          : [...prev, { term_id: r.term_id, name: r.name }]
                      )
                      setTermQuery('')
                      setTermResults([])
                    }}
                  >
                    {r.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-2 mt-4">
          <div className="text-base font-medium text-gray-900">
            Linked Reports
          </div>
          <div className="flex flex-wrap gap-2 mb-2">
            {selectedReports.map((r) => (
              <div
                key={r.report_id}
                className="inline-flex items-center bg-blue-100 text-blue-800 rounded px-3 py-1 text-sm font-medium cursor-move"
              >
                <svg
                  className="w-3 h-3 mr-2 text-blue-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <title>Reorder</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 8h16M4 16h16"
                  />
                </svg>
                {r.title || r.name}
                <button
                  type="button"
                  onClick={() =>
                    setSelectedReports((prev) =>
                      prev.filter((x) => x.report_id !== r.report_id)
                    )
                  }
                  className="ml-2 text-blue-600 hover:text-blue-900 focus:outline-none"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          <div className="relative">
            <input
              className="w-full rounded border border-gray-300 px-4 py-2.5 shadow-inner focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors"
              placeholder="search for reports.."
              value={reportQuery}
              onChange={(e) => {
                const q = e.target.value
                setReportQuery(q)
                void runReportSearch(q)
              }}
            />
            {reportResults.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded shadow-lg max-h-60 overflow-y-auto">
                {reportResults.map((r) => (
                  <button
                    key={r.report_id}
                    type="button"
                    className="w-full text-left px-4 py-2 hover:bg-blue-50 focus:bg-blue-50 outline-none text-sm text-gray-700"
                    onClick={() => {
                      setSelectedReports((prev) =>
                        prev.some((x) => x.report_id === r.report_id)
                          ? prev
                          : [
                              ...prev,
                              {
                                report_id: r.report_id,
                                title: r.title,
                                name: r.name
                              }
                            ]
                      )
                      setReportQuery('')
                      setReportResults([])
                    }}
                  >
                    {r.title || r.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {!session ? (
        <div className="rounded border bg-yellow-50 p-4 text-sm text-yellow-900 mt-6">
          You must be logged in to edit collections.
        </div>
      ) : null}
    </div>
  )
}
