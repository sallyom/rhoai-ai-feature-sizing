import React, { useState, useCallback } from 'react';

const FileUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);

  // Upload API endpoint - determine URL based on environment
  const getUploadApiUrl = () => {
    // In development (localhost), use port-based URL
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return window.location.origin.replace(':3000', ':8001');
    }
    
    // In OpenShift, use the upload route
    const currentHost = window.location.host;
    if (currentHost.includes('rhoai-ui')) {
      // Replace rhoai-ui with rhoai-upload in the hostname
      const uploadHost = currentHost.replace('rhoai-ui', 'rhoai-upload');
      return `${window.location.protocol}//${uploadHost}`;
    }
    
    // Fallback - try to reach upload API on same host with different port
    return window.location.origin.replace(':3000', ':8001');
  };

  const uploadApiUrl = getUploadApiUrl();

  const handleUpload = async (files) => {
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadStatus(null);

    try {
      const formData = new FormData();
      formData.append('file', files[0]);

      const response = await fetch(`${uploadApiUrl}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus({
          type: 'success',
          message: `File "${result.filename}" uploaded successfully!`,
          details: result
        });
        
        // Refresh uploaded files list
        await fetchUploadedFiles();
      } else {
        setUploadStatus({
          type: 'error',
          message: result.detail || 'Upload failed'
        });
      }
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: `Upload error: ${error.message}`
      });
    } finally {
      setIsUploading(false);
    }
  };

  const fetchUploadedFiles = async () => {
    try {
      const response = await fetch(`${uploadApiUrl}/api/uploads`);
      if (response.ok) {
        const data = await response.json();
        setUploadedFiles(data.files || []);
      }
    } catch (error) {
      console.error('Failed to fetch uploaded files:', error);
    }
  };

  const deleteFile = async (filename) => {
    try {
      const response = await fetch(`${uploadApiUrl}/api/uploads/${encodeURIComponent(filename)}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setUploadStatus({
          type: 'success',
          message: `File "${filename}" deleted successfully!`
        });
        await fetchUploadedFiles();
      } else {
        const result = await response.json();
        setUploadStatus({
          type: 'error',
          message: result.detail || 'Delete failed'
        });
      }
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: `Delete error: ${error.message}`
      });
    }
  };

  // Load uploaded files on component mount
  React.useEffect(() => {
    fetchUploadedFiles();
  }, []);

  // Drag and drop handlers
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUpload(e.dataTransfer.files);
    }
  }, []);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleUpload(e.target.files);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="file-upload-container" style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', margin: '10px 0' }}>
      <h3 style={{ marginTop: '0', color: '#333' }}>📁 Upload Knowledge Documents</h3>
      <p style={{ color: '#666', fontSize: '14px' }}>
        Upload documents to enhance agent knowledge bases. Files will be automatically indexed and available for analysis.
      </p>

      {/* Drag & Drop Upload Area */}
      <div
        className={`upload-dropzone ${dragActive ? 'active' : ''}`}
        style={{
          border: `2px dashed ${dragActive ? '#007bff' : '#ccc'}`,
          borderRadius: '8px',
          padding: '40px 20px',
          textAlign: 'center',
          backgroundColor: dragActive ? '#f8f9fa' : '#fafafa',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          marginBottom: '20px'
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          id="file-input"
          type="file"
          style={{ display: 'none' }}
          onChange={handleFileSelect}
          accept=".txt,.md,.pdf,.docx,.doc"
          disabled={isUploading}
        />
        
        {isUploading ? (
          <div>
            <div style={{ fontSize: '24px', marginBottom: '10px' }}>⏳</div>
            <p>Uploading and indexing...</p>
          </div>
        ) : (
          <div>
            <div style={{ fontSize: '48px', marginBottom: '10px' }}>📄</div>
            <p style={{ margin: '10px 0', fontSize: '16px', fontWeight: 'bold' }}>
              {dragActive ? 'Drop files here' : 'Click to select files or drag & drop'}
            </p>
            <p style={{ margin: '0', fontSize: '12px', color: '#888' }}>
              Supported: TXT, MD, PDF, DOC, DOCX
            </p>
          </div>
        )}
      </div>

      {/* Upload Status */}
      {uploadStatus && (
        <div
          style={{
            padding: '12px',
            borderRadius: '6px',
            marginBottom: '15px',
            backgroundColor: uploadStatus.type === 'success' ? '#d4edda' : '#f8d7da',
            color: uploadStatus.type === 'success' ? '#155724' : '#721c24',
            border: `1px solid ${uploadStatus.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`
          }}
        >
          <strong>{uploadStatus.type === 'success' ? '✅' : '❌'} {uploadStatus.message}</strong>
          {uploadStatus.details && uploadStatus.details.indexing_result && (
            <div style={{ marginTop: '8px', fontSize: '12px' }}>
              <p>📊 Indexing Results:</p>
              <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                <li>Documents processed: {uploadStatus.details.indexing_result.total_documents}</li>
                <li>Agents updated: {uploadStatus.details.indexing_result.agents_updated}</li>
                <li>File size: {formatFileSize(uploadStatus.details.file_size)}</li>
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div>
          <h4 style={{ color: '#333', marginBottom: '10px' }}>📋 Uploaded Files ({uploadedFiles.length})</h4>
          <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #eee', borderRadius: '4px' }}>
            {uploadedFiles.map((file, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 12px',
                  borderBottom: index < uploadedFiles.length - 1 ? '1px solid #eee' : 'none',
                  backgroundColor: index % 2 === 0 ? '#fafafa' : '#fff'
                }}
              >
                <div>
                  <strong>{file.filename}</strong>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {formatFileSize(file.size)} • {new Date(file.modified_time).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`Delete "${file.filename}"?`)) {
                      deleteFile(file.filename);
                    }
                  }}
                  style={{
                    background: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '4px 8px',
                    fontSize: '12px',
                    cursor: 'pointer'
                  }}
                  title="Delete file"
                >
                  🗑️ Delete
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Help Text */}
      <div style={{ marginTop: '15px', fontSize: '12px', color: '#666', backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px' }}>
        <strong>💡 How it works:</strong>
        <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
          <li>Upload documents to provide additional context for agent analysis</li>
          <li>Files are automatically processed and added to all 16 agent knowledge bases</li>
          <li>Uploaded content will be available immediately for RFE analysis</li>
          <li>Supported formats: text files, markdown, PDFs, and Word documents</li>
        </ul>
      </div>
    </div>
  );
};

export default FileUpload;