import type { Session } from 'next-auth'

export type AtlasReport = {
  report_id: number
  title: string
  name: string
  description: string
  detailed_description?: string
  system_server?: string
  system_db?: string
  system_table?: string
  system_run_url?: string
  collections?: AtlasCollection[]
}

export type AtlasGroup = {
  group_id: number
  name: string
  account_name: string
  email: string
  group_type: string
}

export type AtlasTerm = {
  term_id: number
  name: string
  summary: string
  technical_definition?: string
  approved_yn?: string
  valid_from?: string | null
  valid_to?: string | null
  collections?: AtlasCollection[]
}

export type AtlasInitiative = {
  initiative_id: number
  name: string
  description: string
  collections?: AtlasCollection[]
}

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

export async function listInitiatives(
  session?: Session | null
): Promise<AtlasInitiative[]> {
  const data = await atlasFetch<
    { results?: AtlasInitiative[] } | AtlasInitiative[]
  >('/api/initiatives/', {
    session,
    cache: 'no-store'
  })

  return Array.isArray(data) ? data : (data.results ?? [])
}

export async function getInitiative(
  session: Session | null,
  id: number
): Promise<AtlasInitiative> {
  return atlasFetch<AtlasInitiative>(`/api/initiatives/${id}/`, {
    session,
    cache: 'no-store'
  })
}

export async function createInitiative(
  session: Session | null,
  data: Pick<AtlasInitiative, 'name' | 'description'>
): Promise<AtlasInitiative> {
  return atlasFetch<AtlasInitiative>('/api/initiatives/', {
    session,
    method: 'POST',
    body: data
  })
}

export async function updateInitiative(
  session: Session | null,
  id: number,
  data: Partial<Pick<AtlasInitiative, 'name' | 'description'>>
): Promise<AtlasInitiative> {
  return atlasFetch<AtlasInitiative>(`/api/initiatives/${id}/`, {
    session,
    method: 'PATCH',
    body: data
  })
}

export async function listTerms(
  session?: Session | null
): Promise<AtlasTerm[]> {
  const data = await atlasFetch<{ results?: AtlasTerm[] } | AtlasTerm[]>(
    '/api/terms/',
    {
      session,
      cache: 'no-store'
    }
  )

  return Array.isArray(data) ? data : (data.results ?? [])
}

export async function getTerm(
  session: Session | null,
  id: number
): Promise<AtlasTerm> {
  return atlasFetch<AtlasTerm>(`/api/terms/${id}/`, {
    session,
    cache: 'no-store'
  })
}

export async function createTerm(
  session: Session | null,
  data: Pick<AtlasTerm, 'name' | 'summary' | 'technical_definition'>
): Promise<AtlasTerm> {
  return atlasFetch<AtlasTerm>('/api/terms/', {
    session,
    method: 'POST',
    body: data
  })
}

export async function updateTerm(
  session: Session | null,
  id: number,
  data: Partial<Pick<AtlasTerm, 'name' | 'summary' | 'technical_definition'>>
): Promise<AtlasTerm> {
  return atlasFetch<AtlasTerm>(`/api/terms/${id}/`, {
    session,
    method: 'PATCH',
    body: data
  })
}

export async function listGroups(
  session?: Session | null
): Promise<AtlasGroup[]> {
  const data = await atlasFetch<{ results?: AtlasGroup[] } | AtlasGroup[]>(
    '/api/groups/',
    {
      session,
      cache: 'no-store'
    }
  )

  return Array.isArray(data) ? data : (data.results ?? [])
}

export async function getGroup(
  session: Session | null,
  id: number
): Promise<AtlasGroup> {
  return atlasFetch<AtlasGroup>(`/api/groups/${id}/`, {
    session,
    cache: 'no-store'
  })
}

export async function createGroup(
  session: Session | null,
  data: Pick<AtlasGroup, 'name' | 'account_name' | 'email' | 'group_type'>
): Promise<AtlasGroup> {
  return atlasFetch<AtlasGroup>('/api/groups/', {
    session,
    method: 'POST',
    body: data
  })
}

export async function listReports(
  session?: Session | null
): Promise<AtlasReport[]> {
  const data = await atlasFetch<{ results?: AtlasReport[] } | AtlasReport[]>(
    '/api/reports/',
    {
      session,
      cache: 'no-store'
    }
  )

  return Array.isArray(data) ? data : (data.results ?? [])
}

export async function getReport(
  session: Session | null,
  id: number
): Promise<AtlasReport> {
  return atlasFetch<AtlasReport>(`/api/reports/${id}/`, {
    session,
    cache: 'no-store'
  })
}

export async function createReport(
  session: Session | null,
  data: Pick<
    AtlasReport,
    'title' | 'name' | 'description' | 'detailed_description'
  >
): Promise<AtlasReport> {
  return atlasFetch<AtlasReport>('/api/reports/', {
    session,
    method: 'POST',
    body: data
  })
}

export async function updateReport(
  session: Session | null,
  id: number,
  data: Partial<
    Pick<AtlasReport, 'title' | 'name' | 'description' | 'detailed_description'>
  >
): Promise<AtlasReport> {
  return atlasFetch<AtlasReport>(`/api/reports/${id}/`, {
    session,
    method: 'PATCH',
    body: data
  })
}

export async function updateGroup(
  session: Session | null,
  id: number,
  data: Partial<
    Pick<AtlasGroup, 'name' | 'account_name' | 'email' | 'group_type'>
  >
): Promise<AtlasGroup> {
  return atlasFetch<AtlasGroup>(`/api/groups/${id}/`, {
    session,
    method: 'PATCH',
    body: data
  })
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
