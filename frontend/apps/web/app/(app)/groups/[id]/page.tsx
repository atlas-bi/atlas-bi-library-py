import { getGroup } from '@/lib/atlas-api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'
import Link from 'next/link'

export default async function GroupDetailsPage({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const groupId = Number(id)
  const session = await getServerSession(authOptions)

  const group = await getGroup(session, groupId)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-6">
        <div className="w-full">
          <h1 className="text-4xl font-light tracking-tight text-gray-900 mb-6">
            {group.name}
          </h1>

          <nav className="breadcrumb text-sm mb-6">
            <ul className="flex items-center space-x-2">
              <li>
                <Link
                  href="#details"
                  className="text-blue-600 hover:text-blue-800"
                >
                  Details
                </Link>
              </li>
            </ul>
          </nav>
        </div>

        <div className="flex flex-col gap-2 flex-shrink-0">
          <Link
            href="/groups"
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors text-center"
          >
            Back
          </Link>
          <Link
            href={`/groups/${group.group_id}/edit`}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors text-center"
          >
            Edit
          </Link>
        </div>
      </div>

      <section id="details" className="mb-8">
        <h2 className="text-3xl font-light text-gray-900 mb-4">Details</h2>

        <div className="mt-8 max-w-2xl">
          <table className="w-full text-[15px] text-left">
            <tbody className="divide-y divide-gray-100 border-t border-b border-gray-100">
              <tr>
                <td className="py-3 font-medium text-gray-900 w-1/3">
                  Account Name
                </td>
                <td className="py-3 text-gray-600">
                  {group.account_name ?? '-'}
                </td>
              </tr>
              <tr>
                <td className="py-3 font-medium text-gray-900 w-1/3">Email</td>
                <td className="py-3 text-gray-600">{group.email ?? '-'}</td>
              </tr>
              <tr>
                <td className="py-3 font-medium text-gray-900 w-1/3">
                  Group Type
                </td>
                <td className="py-3 text-gray-600">
                  {group.group_type ?? '-'}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
