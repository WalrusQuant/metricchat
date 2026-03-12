export interface ReportUser {
  id: string
  name?: string
  email: string
}

export interface ReportDataSource {
  id: string
  name: string
  type: string
}

export interface ReportListItem {
  id: string
  title?: string
  status: string
  slug?: string
  report_type?: string
  user: ReportUser
  data_sources: ReportDataSource[]
  created_at: string
  updated_at?: string
  last_run_at?: string
  cron_schedule?: string
  external_platform?: {
    platform_type: string
  }
  artifact_modes: string[]
  thumbnail_url?: string
  mode?: string
}

export interface PaginationMeta {
  total: number
  page: number
  limit: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ReportListResponse {
  reports: ReportListItem[]
  meta: PaginationMeta
}
