"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Download, FileText, BarChart3, Table } from "lucide-react"
import { LoadingSpinner } from "@/components/loading-spinner"
import { useSuccessNotification } from "@/components/toast-notifications"

interface ExportModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  documentId?: string
  documentTitle?: string
}

export function ExportModal({ open, onOpenChange, documentId, documentTitle }: ExportModalProps) {
  const [exportOptions, setExportOptions] = useState({
    summary: true,
    fullText: false,
    transparencyScore: true,
    charts: true,
    rawData: false,
  })
  const [format, setFormat] = useState("pdf")
  const [isExporting, setIsExporting] = useState(false)
  const [progress, setProgress] = useState(0)

  const showSuccess = useSuccessNotification()

  const handleExport = async () => {
    setIsExporting(true)
    setProgress(0)

    // Simulate export process
    const steps = [
      "Preparing document data...",
      "Generating summary...",
      "Creating visualizations...",
      "Formatting export file...",
      "Finalizing download...",
    ]

    for (let i = 0; i < steps.length; i++) {
      const stepProgress = ((i + 1) / steps.length) * 100

      // Animate progress
      for (let p = progress; p <= stepProgress; p += 2) {
        setProgress(p)
        await new Promise((resolve) => setTimeout(resolve, 30))
      }

      await new Promise((resolve) => setTimeout(resolve, 500))
    }

    setIsExporting(false)
    setProgress(0)
    onOpenChange(false)

    showSuccess("Export complete", `${documentTitle || "Document"} has been exported successfully.`)
  }

  const toggleOption = (option: keyof typeof exportOptions) => {
    setExportOptions((prev) => ({ ...prev, [option]: !prev[option] }))
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Export Document</DialogTitle>
          <DialogDescription>Choose what to include in your export</DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Export Options */}
          <div className="space-y-4">
            <Label className="text-base font-medium">Include in Export</Label>

            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <Checkbox
                  id="summary"
                  checked={exportOptions.summary}
                  onCheckedChange={() => toggleOption("summary")}
                />
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <Label htmlFor="summary" className="text-sm">
                    Executive Summary
                  </Label>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Checkbox
                  id="fullText"
                  checked={exportOptions.fullText}
                  onCheckedChange={() => toggleOption("fullText")}
                />
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <Label htmlFor="fullText" className="text-sm">
                    Full Document Text
                  </Label>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Checkbox
                  id="transparencyScore"
                  checked={exportOptions.transparencyScore}
                  onCheckedChange={() => toggleOption("transparencyScore")}
                />
                <div className="flex items-center space-x-2">
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                  <Label htmlFor="transparencyScore" className="text-sm">
                    Transparency Analysis
                  </Label>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Checkbox id="charts" checked={exportOptions.charts} onCheckedChange={() => toggleOption("charts")} />
                <div className="flex items-center space-x-2">
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                  <Label htmlFor="charts" className="text-sm">
                    Charts & Visualizations
                  </Label>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Checkbox
                  id="rawData"
                  checked={exportOptions.rawData}
                  onCheckedChange={() => toggleOption("rawData")}
                />
                <div className="flex items-center space-x-2">
                  <Table className="h-4 w-4 text-muted-foreground" />
                  <Label htmlFor="rawData" className="text-sm">
                    Raw Data (CSV)
                  </Label>
                </div>
              </div>
            </div>
          </div>

          {/* Format Selection */}
          <div className="space-y-2">
            <Label>Export Format</Label>
            <Select value={format} onValueChange={setFormat}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pdf">PDF Document</SelectItem>
                <SelectItem value="docx">Word Document</SelectItem>
                <SelectItem value="xlsx">Excel Spreadsheet</SelectItem>
                <SelectItem value="zip">ZIP Archive</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Progress */}
          {isExporting && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Exporting...</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} />
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isExporting}>
              Cancel
            </Button>
            <Button onClick={handleExport} disabled={isExporting}>
              {isExporting ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
