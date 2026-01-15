'use client'

import type {
  AtlasCollection,
  AtlasReportSearchResult,
  AtlasTermSearchResult
} from '@/lib/atlas-api'
import type { CollectionUpsertInput } from '@/actions/collections-actions'
import { upsertCollectionAction } from '@/actions/collections-actions'
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

  const [selectedReports, setSelectedReports] = useState<SelectedReport[]>(
    initialReports
  )
  const [selectedTerms, setSelectedTerms] = useState<SelectedTerm[]>(initialTerms)

  const [reportQuery, setReportQuery] = useState('')
  const [termQuery, setTermQuery] = useState('')
  const [reportResults, setReportResults] = useState<AtlasReportSearchResult[]>([])
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
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight text-gray-900">
          {initial ? `Editing ${initial.name}` : 'New Collection'}
        </h1>

        <div className="flex gap-3">
          <Link
            href={initial ? `/collections/${initial.collection_id}` : '/collections'}
            className="rounded-md border bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </Link>
          <button
            type="button"
            onClick={submit}
            disabled={isPending}
            className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
          >
            Save
          </button>
        </div>
      </div>

      <div className="rounded-lg border bg-white p-6">
        <div className="grid gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Name
            </label>
            <input
              className="w-full rounded-md border px-3 py-2"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g Data Sorting"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Purpose
            </label>
            <textarea
              className="w-full rounded-md border px-3 py-2"
              value={searchSummary}
              onChange={(e) => setSearchSummary(e.target.value)}
              rows={4}
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              className="w-full rounded-md border px-3 py-2"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              id="hidden"
              type="checkbox"
              checked={hidden}
              onChange={(e) => setHidden(e.target.checked)}
            />
            <label htmlFor="hidden" className="text-sm text-gray-700">
              Hide Collection?
            </label>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="rounded-lg border bg-white p-6">
          <h2 className="mb-3 text-base font-semibold text-gray-900">
            Linked Terms
          </h2>

          <div className="mb-3 flex flex-wrap gap-2">
            {selectedTerms.map((t) => (
              <button
                key={t.term_id}
                type="button"
                onClick={() =>
                  setSelectedTerms((prev) =>
                    prev.filter((x) => x.term_id !== t.term_id)
                  )
                }
                className="rounded bg-blue-600 px-2 py-1 text-xs text-white"
              >
                {t.name} ×
              </button>
            ))}
          </div>

          <input
            className="w-full rounded-md border px-3 py-2"
            placeholder="search for terms.."
            value={termQuery}
            onChange={(e) => {
              const q = e.target.value
              setTermQuery(q)
              void runTermSearch(q)
            }}
          />

          {termResults.length > 0 ? (
            <div className="mt-2 rounded-md border bg-white">
              {termResults.map((r) => (
                <button
                  key={r.term_id}
                  type="button"
                  className="block w-full px-3 py-2 text-left text-sm hover:bg-gray-50"
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
          ) : null}
        </div>

        <div className="rounded-lg border bg-white p-6">
          <h2 className="mb-3 text-base font-semibold text-gray-900">
            Linked Reports
          </h2>

          <div className="mb-3 flex flex-wrap gap-2">
            {selectedReports.map((r) => (
              <button
                key={r.report_id}
                type="button"
                onClick={() =>
                  setSelectedReports((prev) =>
                    prev.filter((x) => x.report_id !== r.report_id)
                  )
                }
                className="rounded bg-blue-600 px-2 py-1 text-xs text-white"
              >
                {r.title || r.name} ×
              </button>
            ))}
          </div>

          <input
            className="w-full rounded-md border px-3 py-2"
            placeholder="search for reports.."
            value={reportQuery}
            onChange={(e) => {
              const q = e.target.value
              setReportQuery(q)
              void runReportSearch(q)
            }}
          />

          {reportResults.length > 0 ? (
            <div className="mt-2 rounded-md border bg-white">
              {reportResults.map((r) => (
                <button
                  key={r.report_id}
                  type="button"
                  className="block w-full px-3 py-2 text-left text-sm hover:bg-gray-50"
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
          ) : null}
        </div>
      </div>

      {!session ? (
        <div className="rounded-md border bg-yellow-50 p-4 text-sm text-yellow-900">
          You must be logged in to edit collections.
        </div>
      ) : null}
    </div>
  )
}
