import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { AlertTriangle, Shield, Monitor, Globe, Clock } from 'lucide-react';

const DataSection = ({ icon: Icon, title, items }) => (
  <div className="space-y-2">
    <h3 className="flex items-center gap-2 font-bold">
      <Icon className="w-5 h-5" />
      {title}
    </h3>
    <ul className="list-disc pl-5 space-y-1">
      {items.map((item, i) => <li key={i}>{item}</li>)}
    </ul>
  </div>
);

const DataExposureViewer = () => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/get_user_data');
        const data = await response.json();
        setUserData(data);
      } catch (error) {
        console.error('Error fetching user data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading || !userData) return <div>Loading...</div>;

  const sections = [
    {
      icon: Monitor,
      title: 'Your Device & Browser',
      items: [
        `Browser: ${userData.browser_data.browser} ${userData.browser_data.browser_version}`,
        `Operating System: ${userData.browser_data.os}`,
        `Device Type: ${userData.browser_data.device}`,
        `Screen Resolution: ${userData.screen_data.resolution}`,
        `Available Memory: ${userData.system_data.memory_total}`,
        `CPU Cores: ${userData.system_data.cpu_cores}`
      ]
    },
    {
      icon: Globe,
      title: 'Your Location & Network',
      items: [
        `Approximate Location: ${userData.network_data.approximate_location}`,
        `Internet Provider: ${userData.network_data.isp}`,
        `Connection Type: ${userData.network_data.connection_type}`,
        `IP Address: ${userData.network_data.ip_address}`
      ]
    },
    {
      icon: Clock,
      title: 'Time & Language',
      items: [
        `Local Time: ${userData.time_data.local_time}`,
        `Timezone: ${userData.time_data.timezone}`,
        `Language: ${userData.time_data.language}`
      ]
    },
    {
      icon: Shield,
      title: 'Browser Settings',
      items: [
        `Cookies Enabled: ${userData.browser_capabilities.cookies_enabled ? 'Yes' : 'No'}`,
        `Do Not Track: ${userData.browser_capabilities.do_not_track ? 'Enabled' : 'Disabled'}`,
        `Installed Plugins: ${userData.browser_capabilities.plugins.length}`,
        `Detected Fonts: ${userData.browser_capabilities.fonts.length}`
      ]
    }
  ];

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
            {sections.map((section, i) => (
              <DataSection key={i} {...section} />
            ))}
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