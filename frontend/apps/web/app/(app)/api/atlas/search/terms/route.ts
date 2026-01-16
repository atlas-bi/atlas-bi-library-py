import { type AtlasTermSearchResult, atlasFetch } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { NextResponse } from 'next/server'

export async function GET(req: Request) {
  const session = await getServerSession(authOptions)

  if (session === null) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 })
  }

  const { searchParams } = new URL(req.url)
  const q = searchParams.get('q') ?? ''

  const data = await atlasFetch<AtlasTermSearchResult[]>(
    `/api/search/terms/?${new URLSearchParams({ q }).toString()}`,
    {
      session,
      cache: 'no-store'
    }
  )

  return NextResponse.json(data)
}
