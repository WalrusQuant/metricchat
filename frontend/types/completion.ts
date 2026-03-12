export interface CompletionPrompt {
  content: string
}

export interface CompletionContent {
  content?: string
  reasoning?: string
}

export interface CompletionWidget {
  id: string
  title?: string
}

export interface CompletionStep {
  id: string
  status?: string
  slug?: string
  data_model?: {
    type: string
  }
}

export interface CompletionFile {
  id: string
  filename: string
  content_type: string
}

export interface CompletionMessage {
  id: string
  status?: string
  role: string
  prompt?: CompletionPrompt
  completion?: CompletionContent
  widget?: CompletionWidget
  step?: CompletionStep
  sigkill?: boolean | null
  feedback_score?: number
  isCollapsed?: boolean
  files?: CompletionFile[]
}

export interface SelectedWidgetId {
  widgetId: string | null
  stepId: string | null
}
