'use client'

import type { TermUpsertInput } from '@/actions/terms-actions'
import { upsertTermAction } from '@/actions/terms-actions'
import type { AtlasTerm } from '@/lib/atlas-api'
import { useSession } from 'next-auth/react'
import Link from 'next/link'
import { useState, useTransition } from 'react'

export function TermForm({
  initial
}: {
  initial?: AtlasTerm
}) {
  const { data: session } = useSession()
  const [isPending, startTransition] = useTransition()

  const [name, setName] = useState(initial?.name ?? '')
  const [summary, setSummary] = useState(initial?.summary ?? '')
  const [technicalDefinition, setTechnicalDefinition] = useState(
    initial?.technical_definition ?? ''
  )

  function submit() {
    const payload: TermUpsertInput = {
      termId: initial?.term_id,
      name,
      summary,
      technical_definition: technicalDefinition
    }

    startTransition(async () => {
      await upsertTermAction(payload)
    })
  }

  return (
    <div className="flex flex-col gap-6 max-w-5xl">
      <h1 className="text-4xl font-light tracking-tight text-gray-900 mb-2">
        {initial ? `Editing ${initial.name}` : 'New Term'}
      </h1>

      <div className="flex justify-between items-center mb-6">
        <Link
          href={initial ? `/terms/${initial.term_id}` : '/terms'}
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
            htmlFor="term-name"
            className="text-base font-medium text-gray-900"
          >
            Name
          </label>
          <input
            id="term-name"
            className="w-full rounded border border-gray-300 px-4 py-2.5 shadow-inner focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g Inpatient Visit"
            required
          />
        </div>

        <div className="flex flex-col gap-2">
          <label
            htmlFor="term-summary"
            className="text-base font-medium text-gray-900"
          >
            Summary
          </label>
          <textarea
            id="term-summary"
            className="w-full rounded border border-gray-300 px-4 py-3 shadow-inner focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors text-sm"
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            rows={4}
          />
        </div>

        <div className="flex flex-col gap-2">
          <label
            htmlFor="term-technical"
            className="text-base font-medium text-gray-900"
          >
            Technical Definition
          </label>
          <textarea
            id="term-technical"
            className="w-full rounded border border-gray-300 px-4 py-3 shadow-inner focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors font-mono text-sm"
            value={technicalDefinition}
            onChange={(e) => setTechnicalDefinition(e.target.value)}
            rows={6}
          />
        </div>
      </div>

      {!session ? (
        <div className="rounded border bg-yellow-50 p-4 text-sm text-yellow-900 mt-6">
          You must be logged in to edit terms.
        </div>
      ) : null}
    </div>
  )
}
