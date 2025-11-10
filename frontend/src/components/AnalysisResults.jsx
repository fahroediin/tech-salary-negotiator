import React, { useState } from 'react';
import {
  DollarSign, TrendingUp, Target, AlertTriangle, CheckCircle, XCircle,
  FileText, Copy, Download, ArrowLeft, Mail, MessageSquare
} from 'lucide-react';

const AnalysisResults = ({ data, onNewAnalysis }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [activeScript, setActiveScript] = useState('balanced');

  const { offer_data, analysis, scripts } = data;

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'EXCELLENT':
        return 'text-success-600 bg-success-50';
      case 'COMPETITIVE':
        return 'text-primary-600 bg-primary-50';
      case 'FAIR':
        return 'text-warning-600 bg-warning-50';
      case 'UNDERPAID':
        return 'text-orange-600 bg-orange-50';
      case 'SIGNIFICANTLY_UNDERPAID':
        return 'text-danger-600 bg-danger-50';
      case 'BELOW_UMK':
        return 'text-red-700 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getVerdictIcon = (verdict) => {
    switch (verdict) {
      case 'EXCELLENT':
      case 'COMPETITIVE':
        return <CheckCircle className="w-5 h-5" />;
      case 'FAIR':
        return <AlertTriangle className="w-5 h-5" />;
      case 'UNDERPAID':
        return <AlertTriangle className="w-5 h-5" />;
      case 'SIGNIFICANTLY_UNDERPAID':
      case 'BELOW_UMK':
        return <XCircle className="w-5 h-5" />;
      default:
        return <AlertTriangle className="w-5 h-5" />;
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount || 0);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  const downloadScript = (script, title) => {
    const element = document.createElement('a');
    const file = new Blob([script], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${title.replace(/\s+/g, '_')}_negotiation_script.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Verdict */}
      <div className={`p-6 rounded-lg border ${getVerdictColor(analysis.verdict)}`}>
        <div className="flex items-center space-x-3 mb-3">
          {getVerdictIcon(analysis.verdict)}
          <h3 className="text-lg font-semibold">Overall Assessment</h3>
        </div>
        <p className="text-xl font-bold mb-2">{analysis.verdict.replace('_', ' ')}</p>
        <p className="text-sm">
          Based on market data and current compensation trends
        </p>
      </div>

      {/* Compensation Breakdown */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <DollarSign className="w-5 h-5 mr-2" />
            Your Offer
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Base Salary</span>
              <span className="font-medium">{formatCurrency(offer_data.base_salary)}</span>
            </div>
            {offer_data.bonus > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-600">Bonus</span>
                <span className="font-medium">{formatCurrency(offer_data.bonus)}</span>
              </div>
            )}
            {offer_data.equity_value > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-600">Equity (Annual)</span>
                <span className="font-medium">{formatCurrency(offer_data.equity_value)}</span>
              </div>
            )}
            <div className="border-t pt-3 flex justify-between font-semibold text-lg">
              <span>Total Compensation</span>
              <span className="text-blue-600">{formatCurrency(analysis.total_compensation)}</span>
            </div>

            {/* UMK Compliance */}
            {analysis.umk_compliance && (
              <div className="border-t pt-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">vs. UMK ({analysis.umk_compliance.kabupaten_kota || analysis.umk_compliance.provinsi})</span>
                  <span className={`text-sm font-medium ${
                    analysis.umk_compliance.complies ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {analysis.umk_compliance.difference_formatted}
                  </span>
                </div>
                <div className={`text-xs mt-1 p-2 rounded ${
                  analysis.umk_compliance.complies ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
                }`}>
                  {analysis.umk_compliance.message}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2" />
            Market Data
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">25th Percentile</span>
              <span className="font-medium">{formatCurrency(analysis.market_data.p25)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Median (50th)</span>
              <span className="font-medium">{formatCurrency(analysis.market_data.p50)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">75th Percentile</span>
              <span className="font-medium">{formatCurrency(analysis.market_data.p75)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">90th Percentile</span>
              <span className="font-medium">{formatCurrency(analysis.market_data.p90)}</span>
            </div>
            <div className="text-xs text-gray-500 mt-3">
              Based on {analysis.market_data.sample_size} data points
            </div>
          </div>
        </div>
      </div>

      {/* Negotiation Range */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Target className="w-5 h-5 mr-2" />
          Negotiation Targets
        </h3>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Conservative</div>
            <div className="text-lg font-bold text-green-600">
              {formatCurrency(analysis.negotiation_room.conservative)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              +{analysis.negotiation_room.percentage_increase.conservative}%
            </div>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Realistic</div>
            <div className="text-lg font-bold text-blue-600">
              {formatCurrency(analysis.negotiation_room.realistic)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              +{analysis.negotiation_room.percentage_increase.realistic}%
            </div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Aggressive</div>
            <div className="text-lg font-bold text-purple-600">
              {formatCurrency(analysis.negotiation_room.aggressive)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              +{analysis.negotiation_room.percentage_increase.aggressive}%
            </div>
          </div>
        </div>
      </div>

      {/* Key Leverage Points */}
      {analysis.leverage_points && analysis.leverage_points.length > 0 && (
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Your Negotiation Leverage
          </h3>
          <div className="space-y-3">
            {analysis.leverage_points.map((point, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  point.strength === 'strong' ? 'bg-green-500' :
                  point.strength === 'medium' ? 'bg-yellow-500' : 'bg-gray-400'
                }`}></div>
                <div>
                  <div className="font-medium text-gray-900">{point.description}</div>
                  <div className="text-xs text-gray-500 capitalize">{point.strength} leverage</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderAnalysis = () => (
    <div className="bg-white p-6 rounded-lg border">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Detailed Analysis
      </h3>
      <div className="prose max-w-none">
        {analysis.analysis.split('\n').map((paragraph, index) => (
          <p key={index} className="mb-4 text-gray-700 leading-relaxed">
            {paragraph}
          </p>
        ))}
      </div>
    </div>
  );

  const renderScripts = () => (
    <div className="space-y-6">
      {/* Script Selection */}
      <div className="flex space-x-2 mb-6">
        <button
          onClick={() => setActiveScript('assertive')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeScript === 'assertive'
              ? 'bg-red-100 text-red-700 border-red-200'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Assertive
        </button>
        <button
          onClick={() => setActiveScript('balanced')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeScript === 'balanced'
              ? 'bg-blue-100 text-blue-700 border-blue-200'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Balanced (Recommended)
        </button>
        <button
          onClick={() => setActiveScript('humble')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeScript === 'humble'
              ? 'bg-green-100 text-green-700 border-green-200'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Humble
        </button>
      </div>

      {/* Email Template */}
      <div className="bg-white rounded-lg border">
        <div className="border-b px-6 py-4 flex justify-between items-center">
          <h3 className="font-semibold text-gray-900">
            {activeScript.charAt(0).toUpperCase() + activeScript.slice(1)} Negotiation Script
          </h3>
          <div className="flex space-x-2">
            <button
              onClick={() => copyToClipboard(scripts[activeScript])}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              title="Copy to clipboard"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={() => downloadScript(scripts[activeScript], activeScript)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              title="Download as text file"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="p-6">
          <div className="bg-gray-50 rounded p-4 font-mono text-sm text-gray-700 whitespace-pre-wrap">
            {scripts[activeScript]}
          </div>
        </div>
      </div>

      {/* Tips */}
      {scripts.tips && scripts.tips.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h4 className="font-semibold text-blue-900 mb-4 flex items-center">
            <MessageSquare className="w-5 h-5 mr-2" />
            Negotiation Tips
          </h4>
          <div className="space-y-3">
            {scripts.tips.map((tip, index) => (
              <div key={index}>
                <div className="font-medium text-blue-800">{tip.title}</div>
                <div className="text-sm text-blue-700">{tip.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Talking Points */}
      {scripts.talking_points && scripts.talking_points.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Key Talking Points</h4>
          <ul className="space-y-2">
            {scripts.talking_points.map((point, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></div>
                <span className="text-gray-700">{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <button
          onClick={onNewAnalysis}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Analyze Another Offer</span>
        </button>

        <div className="flex space-x-4">
          <div className="text-right">
            <div className="text-sm text-gray-500">Total Compensation</div>
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(analysis.total_compensation)}
            </div>
          </div>
        </div>
      </div>

      {/* Company and Position Info */}
      <div className="bg-white p-6 rounded-lg border mb-6">
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-500">Company</div>
            <div className="font-semibold text-gray-900">
              {offer_data.company || 'Not specified'}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Position</div>
            <div className="font-semibold text-gray-900">
              {offer_data.job_title || 'Not specified'}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Location</div>
            <div className="font-semibold text-gray-900">
              {offer_data.location || 'Not specified'}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'analysis'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Detailed Analysis
          </button>
          <button
            onClick={() => setActiveTab('scripts')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'scripts'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Negotiation Scripts
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mb-8">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'analysis' && renderAnalysis()}
        {activeTab === 'scripts' && renderScripts()}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={onNewAnalysis}
          className="btn btn-outline px-6 py-3"
        >
          Analyze Another Offer
        </button>
        <button
          onClick={() => setActiveTab('scripts')}
          className="btn btn-primary px-6 py-3 flex items-center space-x-2"
        >
          <Mail className="w-4 h-4" />
          <span>Get Negotiation Scripts</span>
        </button>
      </div>
    </div>
  );
};

export default AnalysisResults;