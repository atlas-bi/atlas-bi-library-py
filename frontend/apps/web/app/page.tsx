import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import { HomeTabs } from './home-tabs'

export default async function Home() {
  const session = await getServerSession(authOptions)
  const username = session?.user?.username

  return <HomeTabs username={username} />
}
