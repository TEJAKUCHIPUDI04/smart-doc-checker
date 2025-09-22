import pathway as pw
import requests
from typing import Dict, Any
import asyncio
from datetime import datetime
import json

class PathwayExternalMonitor:
    def __init__(self):
        self.monitored_urls = []
        self.last_content = {}
        
    def add_monitored_url(self, url: str, check_interval: int = 300):
        """Add URL to monitor for changes"""
        self.monitored_urls.append({
            'url': url,
            'check_interval': check_interval,
            'last_check': None
        })
    
    async def start_monitoring(self, callback_func=None):
        """Start monitoring external documents for changes"""
        print("Starting Pathway monitoring for external document updates...")
        
        while True:
            for monitor_config in self.monitored_urls:
                await self._check_url_for_changes(monitor_config, callback_func)
            
            await asyncio.sleep(60)  # Check every minute
    
    async def _check_url_for_changes(self, monitor_config: dict, callback_func=None):
        """Check a specific URL for changes"""
        url = monitor_config['url']
        
        try:
            response = requests.get(url, timeout=10)
            current_content = response.text
            
            # Check if content has changed
            if url in self.last_content:
                if self.last_content[url] != current_content:
                    print(f"🚨 External document updated: {url}")
                    
                    change_data = {
                        'url': url,
                        'change_detected_at': datetime.now().isoformat(),
                        'content_preview': current_content[:500],
                        'trigger_analysis': True
                    }
                    
                    # Call callback function if provided
                    if callback_func:
                        await callback_func(change_data)
            
            # Update stored content
            self.last_content[url] = current_content
            monitor_config['last_check'] = datetime.now()
            
        except Exception as e:
            print(f"Error monitoring {url}: {e}")
    
    def setup_mock_policy_monitor(self):
        """Set up monitoring for a mock college policy page"""
        mock_policy_url = "https://example-college.edu/policies"  # Mock URL
        self.add_monitored_url(mock_policy_url)
        
        # For demonstration, we'll simulate policy changes
        return {
            'monitoring_active': True,
            'monitored_url': mock_policy_url,
            'description': 'Monitoring college policy page for updates',
            'check_interval': '5 minutes'
        }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'monitored_urls_count': len(self.monitored_urls),
            'monitored_urls': [
                {
                    'url': config['url'],
                    'last_check': config['last_check'].isoformat() if config['last_check'] else None
                }
                for config in self.monitored_urls
            ],
            'status': 'active' if self.monitored_urls else 'inactive'
        }
