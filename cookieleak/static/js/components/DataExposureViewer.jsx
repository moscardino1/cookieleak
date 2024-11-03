import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { AlertTriangle, Shield, Monitor, Globe, Clock, Cpu } from 'lucide-react';


const DataExposureViewer = () => {
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);
  
    useEffect(() => {
      // Get additional browser data that can only be collected client-side
      const getBrowserData = () => {
        const plugins = [];
        for (let i = 0; i < navigator.plugins.length; i++) {
          plugins.push(navigator.plugins[i].name);
        }
  
        const fonts = [];
        const testString = "mmmmmmmmmmlli";
        const testSize = "72px";
        const baseFont = "monospace";
        
        const baseFontWidth = getTextWidth(testString, `${testSize} ${baseFont}`);
        
        ["Arial", "Verdana", "Times New Roman", "Courier New"].forEach(font => {
          const width = getTextWidth(testString, `${testSize} ${font}, ${baseFont}`);
          if (width !== baseFontWidth) {
            fonts.push(font);
          }
        });
  
        return { plugins, fonts };
      };
  
      const getTextWidth = (text, font) => {
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        context.font = font;
        return context.measureText(text).width;
      };
  
      // Fetch server-side data and combine with client-side data
      fetch('/get_user_data')
        .then(res => res.json())
        .then(data => {
          const browserData = getBrowserData();
          setUserData({
            ...data,
            browser_capabilities: {
              ...data.browser_capabilities,
              plugins: browserData.plugins,
              fonts: browserData.fonts
            }
          });
          setLoading(false);
        })
        .catch(err => {
          console.error('Error fetching user data:', err);
          setLoading(false);
        });
    }, []);
  
    if (loading) {
      return <div className="text-center p-4">Loading your data exposure profile...</div>;
    }
  
    return (
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="text-red-500" />
              Your Real-Time Data Exposure
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Device & Browser Section */}
              <div className="space-y-2">
                <h3 className="flex items-center gap-2 font-bold">
                  <Monitor className="w-5 h-5" />
                  Your Device & Browser
                </h3>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Browser: {userData.browser_data.browser} {userData.browser_data.browser_version}</li>
                  <li>Operating System: {userData.browser_data.os}</li>
                  <li>Device Type: {userData.browser_data.device}</li>
                  <li>Screen Resolution: {userData.screen_data.resolution}</li>
                  <li>Available Memory: {userData.system_data.memory_total}</li>
                  <li>CPU Cores: {userData.system_data.cpu_cores}</li>
                </ul>
              </div>
  
              {/* Location & Network Section */}
              <div className="space-y-2">
                <h3 className="flex items-center gap-2 font-bold">
                  <Globe className="w-5 h-5" />
                  Your Location & Network
                </h3>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Approximate Location: {userData.network_data.approximate_location}</li>
                  <li>Internet Provider: {userData.network_data.isp}</li>
                  <li>Connection Type: {userData.network_data.connection_type}</li>
                  <li>IP Address: {userData.network_data.ip_address}</li>
                </ul>
              </div>
  
              {/* Time & Language Section */}
              <div className="space-y-2">
                <h3 className="flex items-center gap-2 font-bold">
                  <Clock className="w-5 h-5" />
                  Time & Language
                </h3>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Local Time: {userData.time_data.local_time}</li>
                  <li>Timezone: {userData.time_data.timezone}</li>
                  <li>Language: {userData.time_data.language}</li>
                </ul>
              </div>
  
              {/* Browser Capabilities Section */}
              <div className="space-y-2">
                <h3 className="flex items-center gap-2 font-bold">
                  <Shield className="w-5 h-5" />
                  Browser Settings
                </h3>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Cookies Enabled: {userData.browser_capabilities.cookies_enabled ? 'Yes' : 'No'}</li>
                  <li>Do Not Track: {userData.browser_capabilities.do_not_track ? 'Enabled' : 'Disabled'}</li>
                  <li>Installed Plugins: {userData.browser_capabilities.plugins.length}</li>
                  <li>Detected Fonts: {userData.browser_capabilities.fonts.length}</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
  
        <div className="bg-yellow-50 p-4 rounded-lg">
          <h3 className="font-bold text-yellow-800 mb-2">💡 Why does this matter?</h3>
          <p className="text-yellow-700">
            This information can be used to create a unique "fingerprint" of your device. 
            Websites can track you across the internet even without cookies by combining these details.
            The more unique your configuration, the easier it is to identify you.
          </p>
        </div>
      </div>
    );
  };
  
  export default DataExposureViewer;