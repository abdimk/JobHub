import type { ReactNode } from "react"

export interface Job {
  id: string
  title: string
  company: string
  location: string
  description: string
  salary: string
  postedDate: string
  logo?: ReactNode
  url?: string
}

