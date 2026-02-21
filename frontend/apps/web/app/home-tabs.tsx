'use client'

import { Activity, Bell, Star, Users } from 'lucide-react'
import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'

type TabId = 'stars' | 'subscriptions' | 'run-list' | 'groups'

const TAB_IDS: TabId[] = ['stars', 'subscriptions', 'run-list', 'groups']

function isTabId(value: string): value is TabId {
  return (TAB_IDS as string[]).includes(value)
}

export function HomeTabs({
  username
}: {
  username?: string
}) {
  const initialTab = useMemo<TabId>(() => {
    if (typeof window === 'undefined') {
      return 'stars'
    }

    const hash = window.location.hash.replace('#', '')
    if (hash && isTabId(hash)) {
      return hash
    }

    return 'stars'
  }, [])

  const [activeTab, setActiveTab] = useState<TabId>(initialTab)

  const setTab = (tab: TabId) => {
    setActiveTab(tab)
    if (typeof window !== 'undefined') {
      window.location.hash = tab
    }
  }

  useEffect(() => {
    const onHashChange = () => {
      const hash = window.location.hash.replace('#', '')
      if (hash && isTabId(hash)) {
        setActiveTab(hash)
      }
    }

    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
          Hi{username ? `, ${username}` : ''}!
        </h1>
        <p className="mt-2 text-base text-gray-500">
          Welcome back to Atlas BI Library.
        </p>
      </div>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            type="button"
            onClick={() => setTab('stars')}
            className={`
              flex items-center gap-2 whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors
              ${
                activeTab === 'stars'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }
            `}
          >
            <Star
              className={`h-4 w-4 ${activeTab === 'stars' ? 'text-purple-500' : 'text-gray-400'}`}
            />
            Stars
          </button>

          <button
            type="button"
            onClick={() => setTab('subscriptions')}
            className={`
              flex items-center gap-2 whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors
              ${
                activeTab === 'subscriptions'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }
            `}
          >
            <Bell
              className={`h-4 w-4 ${activeTab === 'subscriptions' ? 'text-purple-500' : 'text-gray-400'}`}
            />
            Subscriptions
          </button>

          <button
            type="button"
            onClick={() => setTab('run-list')}
            className={`
              flex items-center gap-2 whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors
              ${
                activeTab === 'run-list'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }
            `}
          >
            <Activity
              className={`h-4 w-4 ${activeTab === 'run-list' ? 'text-purple-500' : 'text-gray-400'}`}
            />
            Report Runs
          </button>

          <button
            type="button"
            onClick={() => setTab('groups')}
            className={`
              flex items-center gap-2 whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors
              ${
                activeTab === 'groups'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }
            `}
          >
            <Users
              className={`h-4 w-4 ${activeTab === 'groups' ? 'text-purple-500' : 'text-gray-400'}`}
            />
            Groups
          </button>
        </nav>
      </div>

      <div className="mt-4">
        {activeTab === 'stars' && (
          <div className="rounded-xl border border-gray-200 bg-white p-8 text-center shadow-sm">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-purple-50">
              <Star className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="mt-4 text-sm font-semibold text-gray-900">
              No stars yet
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by starring your favorite collections or reports.
            </p>
            <div className="mt-6">
              {username ? (
                <Link
                  href="/collections"
                  className="inline-flex items-center rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-purple-600"
                >
                  Browse Collections
                </Link>
              ) : (
                <Link
                  href="/login"
                  className="inline-flex items-center rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-purple-600"
                >
                  Login to view stars
                </Link>
              )}
            </div>
          </div>
        )}

        {activeTab === 'subscriptions' && (
          <div className="rounded-xl border border-gray-200 bg-white p-8 text-center shadow-sm">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-50">
              <Bell className="h-6 w-6 text-gray-400" />
            </div>
            <h3 className="mt-4 text-sm font-semibold text-gray-900">
              Subscriptions
            </h3>
            <p className="mt-1 text-sm text-gray-500">Coming soon.</p>
          </div>
        )}

        {activeTab === 'run-list' && (
          <div className="rounded-xl border border-gray-200 bg-white p-8 text-center shadow-sm">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-50">
              <Activity className="h-6 w-6 text-gray-400" />
            </div>
            <h3 className="mt-4 text-sm font-semibold text-gray-900">
              Report Runs
            </h3>
            <p className="mt-1 text-sm text-gray-500">Coming soon.</p>
          </div>
        )}

        {activeTab === 'groups' && (
          <div className="rounded-xl border border-gray-200 bg-white p-8 text-center shadow-sm">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-50">
              <Users className="h-6 w-6 text-gray-400" />
            </div>
            <h3 className="mt-4 text-sm font-semibold text-gray-900">Groups</h3>
            <p className="mt-1 text-sm text-gray-500">Coming soon.</p>
          </div>
        )}
      </div>
    </div>
  )
}
