import type { ReactNode } from 'react'

export function PageHeader({
  title,
  subtitle,
  right,
}: {
  title: string
  subtitle?: string
  right?: ReactNode
}) {
  return (
    <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <h1 className="text-xl font-semibold text-white">{title}</h1>
        {subtitle ? <p className="mt-1 text-sm text-zinc-400">{subtitle}</p> : null}
      </div>
      {right ? <div className="flex items-center gap-2">{right}</div> : null}
    </div>
  )
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={['rounded-xl border border-zinc-800 bg-zinc-950 p-4', className || ''].join(' ')}>
      {children}
    </div>
  )
}

export function Label({ children }: { children: ReactNode }) {
  return <div className="text-xs font-medium text-zinc-300">{children}</div>
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={[
        'w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-white placeholder:text-zinc-600',
        'focus:outline-none focus:ring-2 focus:ring-violet-500/50',
        props.className || '',
      ].join(' ')}
    />
  )
}

export function Button(props: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'ghost' }) {
  const variant = props.variant || 'primary'
  return (
    <button
      {...props}
      className={[
        'rounded-lg px-3 py-2 text-sm font-medium transition disabled:opacity-60',
        variant === 'primary'
          ? 'bg-violet-600 text-white hover:bg-violet-500'
          : 'border border-zinc-800 bg-transparent text-zinc-200 hover:bg-zinc-900',
        props.className || '',
      ].join(' ')}
    />
  )
}

export function Table({ children }: { children: ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-zinc-800">
      <table className="min-w-full text-left text-sm">{children}</table>
    </div>
  )
}

