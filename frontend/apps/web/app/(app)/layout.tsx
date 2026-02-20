export default async function AppLayout({
  children
}: {
  children: React.ReactNode
}) {
  return <div className="container mx-auto my-12 max-w-6xl">{children}</div>
}
