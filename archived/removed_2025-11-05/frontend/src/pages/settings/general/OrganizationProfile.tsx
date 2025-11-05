import React, { useState } from 'react';
import { ArrowLeft, Building, Save, Upload, Mail, Phone, MapPin, Globe, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const OrganizationProfile: React.FC = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState({
    companyName: 'TSH Travel & Tourism LLC',
    legalName: 'TSH Travel and Tourism Limited Liability Company',
    industry: 'Travel & Tourism',
    taxId: '100123456700003',
    registrationNumber: 'CN-1234567',
    email: 'info@tsh-travel.com',
    phone: '+971 4 123 4567',
    mobile: '+971 50 123 4567',
    website: 'www.tsh-travel.com',
    address: 'Sheikh Zayed Road, Business Bay',
    city: 'Dubai',
    state: 'Dubai',
    postalCode: '12345',
    country: 'United Arab Emirates',
    established: '2015-01-01',
    fiscalYearStart: '01',
    fiscalYearEnd: '12',
    currency: 'AED',
    timezone: 'Asia/Dubai',
    language: 'en',
  });

  const handleSave = () => {
    console.log('Saving organization profile:', profile);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/settings')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Settings
          </button>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-orange-500 rounded-xl">
              <Building className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Organization Profile</h1>
              <p className="text-gray-600">Company information and business details</p>
            </div>
          </div>
        </div>

        {/* Logo Upload */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Company Logo</h3>
          <div className="flex items-center gap-6">
            <div className="w-32 h-32 bg-gradient-to-br from-orange-100 to-orange-200 rounded-xl flex items-center justify-center">
              <Building className="w-16 h-16 text-orange-500" />
            </div>
            <div>
              <button className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors flex items-center gap-2 mb-2">
                <Upload className="w-4 h-4" />
                Upload Logo
              </button>
              <p className="text-sm text-gray-600">
                Recommended size: 512x512px<br />
                Formats: PNG, JPG, SVG (Max 2MB)
              </p>
            </div>
          </div>
        </div>

        {/* Company Information */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Company Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Name
              </label>
              <input
                type="text"
                value={profile.companyName}
                onChange={(e) => setProfile({ ...profile, companyName: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Legal Name
              </label>
              <input
                type="text"
                value={profile.legalName}
                onChange={(e) => setProfile({ ...profile, legalName: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Industry
              </label>
              <select
                value={profile.industry}
                onChange={(e) => setProfile({ ...profile, industry: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option>Travel & Tourism</option>
                <option>Retail</option>
                <option>Manufacturing</option>
                <option>Technology</option>
                <option>Services</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tax ID / VAT Number
              </label>
              <input
                type="text"
                value={profile.taxId}
                onChange={(e) => setProfile({ ...profile, taxId: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Registration Number
              </label>
              <input
                type="text"
                value={profile.registrationNumber}
                onChange={(e) => setProfile({ ...profile, registrationNumber: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                Established Date
              </label>
              <input
                type="date"
                value={profile.established}
                onChange={(e) => setProfile({ ...profile, established: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Contact Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="w-4 h-4 inline mr-1" />
                Email Address
              </label>
              <input
                type="email"
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Phone className="w-4 h-4 inline mr-1" />
                Phone Number
              </label>
              <input
                type="tel"
                value={profile.phone}
                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mobile Number
              </label>
              <input
                type="tel"
                value={profile.mobile}
                onChange={(e) => setProfile({ ...profile, mobile: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Globe className="w-4 h-4 inline mr-1" />
                Website
              </label>
              <input
                type="url"
                value={profile.website}
                onChange={(e) => setProfile({ ...profile, website: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Address */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">
            <MapPin className="w-5 h-5 inline mr-2" />
            Business Address
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Street Address
              </label>
              <input
                type="text"
                value={profile.address}
                onChange={(e) => setProfile({ ...profile, address: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">City</label>
              <input
                type="text"
                value={profile.city}
                onChange={(e) => setProfile({ ...profile, city: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">State/Emirate</label>
              <input
                type="text"
                value={profile.state}
                onChange={(e) => setProfile({ ...profile, state: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Postal Code</label>
              <input
                type="text"
                value={profile.postalCode}
                onChange={(e) => setProfile({ ...profile, postalCode: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Country</label>
              <input
                type="text"
                value={profile.country}
                onChange={(e) => setProfile({ ...profile, country: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Regional Settings */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Regional Settings</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
              <select
                value={profile.currency}
                onChange={(e) => setProfile({ ...profile, currency: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value="AED">AED - UAE Dirham</option>
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="GBP">GBP - British Pound</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
              <select
                value={profile.timezone}
                onChange={(e) => setProfile({ ...profile, timezone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value="Asia/Dubai">Asia/Dubai (GMT+4)</option>
                <option value="Europe/London">Europe/London (GMT+0)</option>
                <option value="America/New_York">America/New_York (GMT-5)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
              <select
                value={profile.language}
                onChange={(e) => setProfile({ ...profile, language: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value="en">English</option>
                <option value="ar">العربية (Arabic)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            className="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors flex items-center gap-2 text-lg font-semibold"
          >
            <Save className="w-5 h-5" />
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default OrganizationProfile;
