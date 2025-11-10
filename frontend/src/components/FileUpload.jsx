import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { salaryApi } from '../services/api';

const FileUpload = ({ onAnalysisComplete, onAnalysisStart, onError }) => {
  const [file, setFile] = useState(null);
  const [formData, setFormData] = useState({
    yearsExperience: '',
    techStack: '',
    currentSalary: '',
    hasCompetingOffers: false
  });
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (selectedFile) => {
    if (selectedFile) {
      // Validate file type
      if (selectedFile.type !== 'application/pdf') {
        onError('Please upload a PDF file');
        return;
      }

      // Validate file size (10MB max)
      if (selectedFile.size > 10 * 1024 * 1024) {
        onError('File size must be less than 10MB');
        return;
      }

      setFile(selectedFile);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      onError('Please upload your offer letter');
      return;
    }

    if (!formData.yearsExperience) {
      onError('Please enter your years of experience');
      return;
    }

    if (!formData.techStack) {
      onError('Please enter your tech stack');
      return;
    }

    setIsUploading(true);
    onAnalysisStart();

    try {
      // Create form data for API
      const requestFormData = new FormData();
      requestFormData.append('file', file);
      requestFormData.append('years_experience', formData.yearsExperience);
      requestFormData.append('tech_stack', formData.techStack);

      if (formData.currentSalary) {
        requestFormData.append('current_salary', formData.currentSalary);
      }

      requestFormData.append('has_competing_offers', formData.hasCompetingOffers);

      // Make API call
      const response = await salaryApi.analyzeOffer(requestFormData);

      if (response.success) {
        onAnalysisComplete(response.data);
      } else {
        onError(response.message || 'Analysis failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      onError(error.message || 'Failed to analyze offer. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* File Upload Area */}
        <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 p-8">
          <div
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDrag}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
          >
            {file ? (
              <div className="flex items-center justify-center space-x-3">
                <FileText className="w-8 h-8 text-green-600" />
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="ml-4 text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
            ) : (
              <div>
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="mt-4">
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <span className="mt-2 block text-sm font-medium text-gray-900">
                      Drop your offer letter here, or{' '}
                      <span className="text-primary-600 hover:text-primary-500">
                        browse
                      </span>
                    </span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept=".pdf"
                      onChange={(e) => handleFileChange(e.target.files[0])}
                    />
                  </label>
                  <p className="mt-1 text-xs text-gray-500">
                    PDF files up to 10MB
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Additional Information */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            Additional Information
          </h3>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Years of Experience */}
            <div>
              <label htmlFor="yearsExperience" className="form-label">
                Years of Experience *
              </label>
              <input
                type="number"
                id="yearsExperience"
                name="yearsExperience"
                min="0"
                max="50"
                step="0.5"
                value={formData.yearsExperience}
                onChange={handleInputChange}
                className="form-input"
                placeholder="e.g., 5"
                required
              />
            </div>

            {/* Current Salary */}
            <div>
              <label htmlFor="currentSalary" className="form-label">
                Current Salary (optional)
              </label>
              <input
                type="number"
                id="currentSalary"
                name="currentSalary"
                min="0"
                step="1000"
                value={formData.currentSalary}
                onChange={handleInputChange}
                className="form-input"
                placeholder="e.g., 85000"
              />
            </div>

            {/* Tech Stack */}
            <div className="md:col-span-2">
              <label htmlFor="techStack" className="form-label">
                Tech Stack *
              </label>
              <input
                type="text"
                id="techStack"
                name="techStack"
                value={formData.techStack}
                onChange={handleInputChange}
                className="form-input"
                placeholder="e.g., Python, JavaScript, React, AWS"
                required
              />
              <p className="mt-1 text-xs text-gray-500">
                Separate technologies with commas
              </p>
            </div>

            {/* Competing Offers */}
            <div className="md:col-span-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="hasCompetingOffers"
                  name="hasCompetingOffers"
                  checked={formData.hasCompetingOffers}
                  onChange={handleInputChange}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">
                  I have competing offers
                </span>
              </label>
              <p className="mt-1 text-xs text-gray-500">
                This can help with negotiations
              </p>
            </div>
          </div>
        </div>

        {/* Privacy Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Privacy & Security</p>
              <p>
                Your offer letter and personal information are processed securely and are
                only used for generating your salary analysis. We do not store your documents
                or share your data with third parties.
              </p>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-center">
          <button
            type="submit"
            disabled={isUploading || !file}
            className="btn btn-primary px-8 py-3 text-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? (
              <div className="flex items-center space-x-2">
                <div className="loading-spinner w-5 h-5"></div>
                <span>Analyzing Offer...</span>
              </div>
            ) : (
              'Analyze My Offer'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FileUpload;