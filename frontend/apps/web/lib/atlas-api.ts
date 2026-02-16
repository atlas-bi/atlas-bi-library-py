import type { Session } from 'next-auth'

export type AtlasCollection = {
  collection_id: number
  name: string
  search_summary: string
  description: string
  hidden: string
  modified_at: string | null
  initiative?: {
    initiative_id: number
    name: string
    description: string
  } | null
  reports?: AtlasCollectionReportLink[]
  terms?: AtlasCollectionTermLink[]
}

export type AtlasCollectionReportLink = {
  link_id: number
  rank: number | null
  report: { report_id: number; title: string; name: string }
  report_id?: number
}

export type AtlasCollectionTermLink = {
  link_id: number
  rank: number | null
  term: { term_id: number; name: string; summary?: string }
  term_id?: number
}

export type AtlasReportSearchResult = {
  report_id: number
  title: string
  name: string
}

export type AtlasTermSearchResult = {
  term_id: number
  name: string
}

function getBaseUrl() {
  const base = process.env.API_URL
  if (!base) {
    throw new Error('API_URL is not set')
  }
  return base.replace(/\/$/, '')
}

function authHeader(session?: Session | null) {
  const headers: Record<string, string> = {}

  if (session?.accessToken) {
    headers.Authorization = `Bearer ${session.accessToken}`
  }

  return headers
}

type NextFetchOptions = {
  revalidate?: number | false
  tags?: string[]
}

export async function atlasFetch<T>(
  path: string,
  opts: {
    session?: Session | null
    method?: string
    body?: unknown
    cache?: RequestCache
    next?: NextFetchOptions
  } = {}
): Promise<T> {
  const url = `${getBaseUrl()}${path.startsWith('/') ? '' : '/'}${path}`

  const init: RequestInit & { next?: NextFetchOptions } = {
    method: opts.method ?? (opts.body ? 'POST' : 'GET'),
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(opts.session)
    } satisfies HeadersInit,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
    cache: opts.cache
  }

  if (opts.next != null) {
    init.next = opts.next
  }

  const res = await fetch(url, init)

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`API ${res.status}: ${text || res.statusText}`)
  }

  if (res.status === 204) {
    return undefined as T
  }

  return (await res.json()) as T
}

export async function listCollections(
  session?: Session | null
): Promise<AtlasCollection[]> {
  const data = await atlasFetch<
    { results?: AtlasCollection[] } | AtlasCollection[]
  >('/api/collections/', {
    session,
    cache: 'no-store'
  })

  return Array.isArray(data) ? data : (data.results ?? [])
}

export async function getCollection(
  session: Session | null,
  id: number
): Promise<AtlasCollection> {
  return atlasFetch<AtlasCollection>(`/api/collections/${id}/`, {
    session,
    cache: 'no-store'
  })
}

export async function createCollection(
  session: Session | null,
  data: Pick<
    AtlasCollection,
    'name' | 'search_summary' | 'description' | 'hidden'
  >
): Promise<AtlasCollection> {
  return atlasFetch<AtlasCollection>('/api/collections/', {
    session,
    method: 'POST',
    body: data
  })
}

export async function updateCollection(
  session: Session | null,
  id: number,
  data: Partial<
    Pick<AtlasCollection, 'name' | 'search_summary' | 'description' | 'hidden'>
  >
): Promise<AtlasCollection> {
  return atlasFetch<AtlasCollection>(`/api/collections/${id}/`, {
    session,
    method: 'PATCH',
    body: data
  })
}

export async function setCollectionLinks(
  session: Session | null,
  id: number,
  body: { report_ids: number[]; term_ids: number[] }
): Promise<AtlasCollection> {
  return atlasFetch<AtlasCollection>(`/api/collections/${id}/set-links/`, {
    session,
    method: 'POST',
    body
  })
}

export async function searchReports(
  session: Session | null,
  q: string
): Promise<AtlasReportSearchResult[]> {
  const qp = new URLSearchParams({ q })
  return atlasFetch<AtlasReportSearchResult[]>(
    `/api/search/reports/?${qp.toString()}`,
    {
      session,
      cache: 'no-store'
    }
  )
}

export async function searchTerms(
  session: Session | null,
  q: string
): Promise<AtlasTermSearchResult[]> {
  const qp = new URLSearchParams({ q })
  return atlasFetch<AtlasTermSearchResult[]>(
    `/api/search/terms/?${qp.toString()}`,
    {
      session,
      cache: 'no-store'
    }
  )
}
