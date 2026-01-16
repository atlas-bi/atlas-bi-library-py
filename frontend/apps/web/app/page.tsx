import { UserSession } from '@/components/user-session'
import Link from 'next/link'

export default function Home() {
  return (
    <>
      <h1 className="text-2xl font-semibold tracking-tight text-gray-900">
        Hi!
      </h1>

      <UserSession />

      <hr className="my-8" />

      <nav className="mb-8">
        <ul className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
          <li>
            <a className="text-purple-600 underline" href="#stars">
              Stars
            </a>
          </li>
          <li>
            <a className="text-purple-600 underline" href="#subscriptions">
              Subscriptions
            </a>
          </li>
          <li>
            <a className="text-purple-600 underline" href="#run-list">
              Report Runs
            </a>
          </li>
          <li>
            <a className="text-purple-600 underline" href="#groups">
              Groups
            </a>
          </li>
        </ul>
      </nav>

      <section className="flex flex-col gap-10">
        <div id="stars" className="scroll-mt-24">
          <h2 className="text-lg font-semibold text-gray-900">Stars</h2>
          <p className="mt-1 text-sm text-gray-600">
            In the legacy app this shows your starred items. In Turbo, start with
            Collections.
          </p>
          <div className="mt-3">
            <Link href="/collections" className="text-purple-600 underline">
              Go to Collections
            </Link>
          </div>
        </div>

        <div id="subscriptions" className="scroll-mt-24">
          <h2 className="text-lg font-semibold text-gray-900">Subscriptions</h2>
          <p className="mt-1 text-sm text-gray-600">Coming soon.</p>
        </div>

        <div id="run-list" className="scroll-mt-24">
          <h2 className="text-lg font-semibold text-gray-900">Report Runs</h2>
          <p className="mt-1 text-sm text-gray-600">Coming soon.</p>
        </div>

        <div id="groups" className="scroll-mt-24">
          <h2 className="text-lg font-semibold text-gray-900">Groups</h2>
          <p className="mt-1 text-sm text-gray-600">Coming soon.</p>
        </div>
      </section>
    </>
  )
}
