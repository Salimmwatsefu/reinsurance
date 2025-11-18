import { useState, useCallback } from 'react';
import { useLocation } from 'wouter';
import DashboardLayout from '@/components/DashboardLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { api } from '@/lib/api';

export default function UploadClaim() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [, setLocation] = useLocation();

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
      setUploadResult(null);
    } else {
      toast.error('Please upload a PDF file');
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    try {
      const result = await api.uploadClaim(file);
      setUploadResult(result);
      toast.success('Claim processed successfully!');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setUploadResult(null);
  };

  const handleViewClaim = () => {
    if (uploadResult?.claim?.id) {
      setLocation(`/claims/${uploadResult.claim.id}`);
    }
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="max-w-4xl mx-auto space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Upload Claim</h1>
            <p className="text-muted-foreground mt-2">
              Upload a claim PDF for automated processing and fraud detection
            </p>
          </div>

          {!uploadResult ? (
            <Card>
              <CardHeader>
                <CardTitle>Select Claim Document</CardTitle>
                <CardDescription>
                  Upload a PDF file containing claim information
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Drag and drop area */}
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                    isDragging
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-lg font-medium text-foreground mb-2">
                    {file ? file.name : 'Drag and drop your PDF here'}
                  </p>
                  <p className="text-sm text-muted-foreground mb-4">or</p>
                  <label htmlFor="file-upload">
                    <Button variant="outline" type="button" asChild>
                      <span>Browse Files</span>
                    </Button>
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>

                {/* File info */}
                {file && (
                  <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                    <FileText className="h-8 w-8 text-primary" />
                    <div className="flex-1">
                      <p className="font-medium text-foreground">{file.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <Button variant="outline" size="sm" onClick={handleReset}>
                      Remove
                    </Button>
                  </div>
                )}

                {/* Upload button */}
                <Button
                  onClick={handleUpload}
                  disabled={!file || isUploading}
                  className="w-full"
                  size="lg"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Processing Claim...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-5 w-5" />
                      Upload and Process
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-8 w-8 text-success" />
                  <div>
                    <CardTitle>Claim Processed Successfully</CardTitle>
                    <CardDescription>
                      Your claim has been analyzed and processed
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Claim info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Claim ID</p>
                    <p className="text-lg font-semibold text-foreground">
                      #{uploadResult.claim.id}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Status</p>
                    <p className="text-lg font-semibold text-foreground capitalize">
                      {uploadResult.claim.status}
                    </p>
                  </div>
                </div>

                {/* Prediction results */}
                {uploadResult.claim.prediction && (
                  <div className="space-y-4">
                    <h3 className="font-semibold text-foreground">Analysis Results</h3>
                    
                    {/* Fraud detection */}
                    <div className={`p-4 rounded-lg border-2 ${
                      uploadResult.claim.prediction.is_fraudulent
                        ? 'bg-warning/5 border-warning'
                        : 'bg-success/5 border-success'
                    }`}>
                      <div className="flex items-center gap-3 mb-2">
                        <AlertCircle className={`h-5 w-5 ${
                          uploadResult.claim.prediction.is_fraudulent
                            ? 'text-warning'
                            : 'text-success'
                        }`} />
                        <p className="font-semibold text-foreground">
                          {uploadResult.claim.prediction.is_fraudulent
                            ? 'Potential Fraud Detected'
                            : 'No Fraud Detected'}
                        </p>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Fraud Score: {(uploadResult.claim.prediction.fraud_score * 100).toFixed(1)}%
                      </p>
                    </div>

                    {/* Reserve estimate */}
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Estimated Reserve
                      </p>
                      <p className="text-2xl font-bold text-foreground">
                        ${uploadResult.claim.prediction.reserve_estimate?.toLocaleString() || 'N/A'}
                      </p>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                  <Button onClick={handleViewClaim} className="flex-1">
                    View Claim Details
                  </Button>
                  <Button onClick={handleReset} variant="outline" className="flex-1">
                    Upload Another
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
