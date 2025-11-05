# TDS Dashboard

Real-time monitoring dashboard for TSH DataSync Core (TDS Core).

## Features

### 1. System Health Monitoring
- **Overall System Status**: Real-time health indicator (Healthy/Degraded/Unhealthy)
- **System Uptime**: Track how long TDS Core has been running
- **Database Status**: Monitor database connection and response times
- **Processing Rate**: Events completed per hour
- **Failed Events Counter**: Quick view of events requiring attention

### 2. Queue Monitor
- **Queue Statistics by Status**:
  - Pending events
  - Currently processing
  - Completed events
  - Failed events
  - Retry queue
  - Dead letter queue
- **Processing Rate**: Events per minute/hour/24 hours
- **Oldest Pending Event Alert**: Warns about stuck events

### 3. Visual Analytics
- **Entity Distribution Chart**: Bar chart showing event distribution by entity type
  - Products
  - Customers
  - Invoices
  - Bills
  - Credit Notes
  - Stock Adjustments
  - Price Lists
  - And more...

- **Processing Rate Over Time**: Real-time line chart tracking throughput

### 4. Real-time Updates
- Auto-refresh every 5 seconds
- Live status indicator
- Smooth animations and transitions

## Tech Stack

- **Frontend**: React 19 + TypeScript
- **Build Tool**: Vite 7
- **Styling**: TailwindCSS 4
- **Data Fetching**: TanStack React Query (v5)
- **Charts**: Recharts
- **Icons**: Lucide React
- **Date Handling**: date-fns

## Configuration

Create a `.env.local` file with:

```env
VITE_TDS_API_URL=http://localhost:8001
VITE_TDS_API_REFRESH_INTERVAL=5000
```

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## API Endpoints Used

- `GET /health` - System health status
- `GET /queue/stats` - Queue statistics
- `GET /webhooks/health` - Webhook health check
- `GET /ping` - Connectivity test

## Dashboard Sections

### Header
- TDS branding with Activity icon
- Live status indicator with spinning refresh icon

### Main Content
1. **System Health Cards** (4 cards)
   - Uptime
   - Database Status
   - Processing Rate
   - Failed Events

2. **Queue Status Cards** (6 cards)
   - Visual representation of each queue status
   - Color-coded for quick status recognition

3. **Charts Section** (2 charts)
   - Entity Distribution (Bar Chart)
   - Processing Rate (Line Chart)

### Footer
- Copyright and branding

## Color Coding

- **Green**: Healthy, Completed, Connected
- **Blue**: Pending, Info
- **Purple**: Processing
- **Yellow**: Degraded, Warning, Retry
- **Red**: Failed, Unhealthy, Error
- **Orange**: Retry queue
- **Gray**: Dead Letter, Archived

## Responsive Design

- Mobile-first approach
- Responsive grid layouts
- Breakpoints:
  - `sm`: 640px
  - `md`: 768px
  - `lg`: 1024px

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Production Deployment

1. Build the dashboard:
   ```bash
   npm run build
   ```

2. The build output will be in `dist/`

3. Serve with any static file server or integrate with TDS Core

## Future Enhancements

- [ ] Alert history viewer
- [ ] Dead letter queue management UI
- [ ] Manual event replay controls
- [ ] Advanced filtering and search
- [ ] Export data to CSV/Excel
- [ ] Webhook configuration UI
- [ ] Real-time notifications (toast messages)
- [ ] Dark mode support
- [ ] User authentication integration
- [ ] Historical data trends (longer time ranges)
- [ ] Performance metrics dashboard
