"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { Upload, FileText, X } from "lucide-react"
import { LoadingSpinner } from "@/components/loading-spinner"
import { useSuccessNotification, useErrorNotification } from "@/components/toast-notifications"

export function UploadModule() {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [county, setCounty] = useState("")
  const [year, setYear] = useState("")
  const [processingStep, setProcessingStep] = useState("")

  const showSuccess = useSuccessNotification()
  const showError = useErrorNotification()

  const counties = ["Nairobi", "Mombasa", "Kisumu", "Nakuru"]
  const years = ["2024", "2023", "2022"]

  // Handle drag and drop
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const droppedFiles = Array.from(e.dataTransfer.files).filter((file) => file.type === "application/pdf")
    if (droppedFiles.length > 0) {
      setFiles((prev) => [...prev, ...droppedFiles])
      showSuccess("Files added", `${droppedFiles.length} PDF(s) ready for upload`)
    } else {
      showError("Invalid file type", "Only PDFs allowed")
    }
  }, [showSuccess, showError])

  // Handle manual file input
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files).filter((file) => file.type === "application/pdf")
      if (selectedFiles.length > 0) {
        setFiles((prev) => [...prev, ...selectedFiles])
        showSuccess("Files selected", `${selectedFiles.length} PDF(s) ready for upload`)
      }
    }
  }

  // Remove one file
  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  // Upload to API
  const simulateUpload = async () => {
  if (!county || !year || files.length === 0) {
    showError("Missing info", "Select county, year, and at least one file")
    return
  }

  setUploading(true)
  setProgress(10)
  setProcessingStep("Uploading to server...")

  const formData = new FormData()
  formData.append("county", county)
  formData.append("year", year)
  files.forEach((file) => formData.append("files", file))

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    })

    const data = await res.json()
    if (data.success) {
      showSuccess("Upload complete", `${files.length} file(s) uploaded successfully`)
    } else {
      showError("Server error", data.error || "Failed to upload")
    }
  } catch (err) {
    console.error("Upload error:", err)
    showError("Network error", "Could not reach server")
  }

  setUploading(false)
  setProgress(0)
  setProcessingStep("")
  setFiles([])
  setCounty("")
  setYear("")
}


  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Documents</CardTitle>
        <CardDescription>Choose county, year, and upload PDF files</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* County selector */}
        <div className="space-y-2">
          <Label>County</Label>
          <Select value={county} onValueChange={setCounty}>
            <SelectTrigger>
              <SelectValue placeholder="Select county" />
            </SelectTrigger>
            <SelectContent>
              {counties.map((c) => (
                <SelectItem key={c} value={c}>{c}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Year selector */}
        <div className="space-y-2">
          <Label>Year</Label>
          <Select value={year} onValueChange={setYear}>
            <SelectTrigger>
              <SelectValue placeholder="Select year" />
            </SelectTrigger>
            <SelectContent>
              {years.map((y) => (
                <SelectItem key={y} value={y}>{y}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Drag & Drop zone */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer"
        >
          <p className="text-sm text-muted-foreground">Drag & drop PDF files here</p>
          <p className="text-xs">or</p>
          <Input type="file" accept="application/pdf" multiple onChange={handleFileInput} />
        </div>

        {/* Files list */}
        {files.length > 0 && (
          <div className="space-y-2">
            {files.map((file, i) => (
              <div key={i} className="flex items-center justify-between border rounded p-2">
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4" />
                  <span>{file.name}</span>
                </div>
                <Button variant="ghost" size="sm" onClick={() => removeFile(i)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}

        {/* Progress bar */}
        {uploading && (
          <div className="space-y-2">
            <Progress value={progress} />
            <p className="text-xs">{processingStep}</p>
          </div>
        )}

        {/* Upload button */}
        <div className="flex justify-end">
          <Button
            onClick={simulateUpload}
            disabled={uploading || files.length === 0 || !county || !year}
            className="min-w-32"
          >
            {uploading ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Processing
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Upload & Process
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
