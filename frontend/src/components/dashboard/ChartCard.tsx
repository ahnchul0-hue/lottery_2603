import type { ReactNode } from 'react'

export function ChartCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="bg-card rounded-xl border border-border p-4">
      <h3 className="text-base font-bold text-text-primary mb-4">{title}</h3>
      {children}
    </section>
  )
}
