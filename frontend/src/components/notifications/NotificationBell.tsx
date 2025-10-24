import React, { useState, useEffect, useCallback } from 'react';
import { IconButton, Badge, Tooltip } from '@mui/material';
import { Notifications as NotificationsIcon } from '@mui/icons-material';
import NotificationCenter from './NotificationCenter';
import notificationService from '../../services/notificationService';

interface NotificationBellProps {
  autoRefresh?: boolean;
  refreshInterval?: number; // in milliseconds
}

const NotificationBell: React.FC<NotificationBellProps> = ({
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds default
}) => {
  const [open, setOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  // Fetch unread count
  const fetchUnreadCount = useCallback(async () => {
    try {
      const count = await notificationService.getUnreadCount();
      setUnreadCount(count);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchUnreadCount();
  }, [fetchUnreadCount]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchUnreadCount();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchUnreadCount]);

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    // Refresh count when closing the drawer
    fetchUnreadCount();
  };

  const handleUnreadCountChange = (count: number) => {
    setUnreadCount(count);
  };

  return (
    <>
      <Tooltip title="Notifications">
        <IconButton color="inherit" onClick={handleOpen}>
          <Badge
            badgeContent={unreadCount}
            color="error"
            max={99}
            overlap="circular"
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <NotificationsIcon />
          </Badge>
        </IconButton>
      </Tooltip>

      <NotificationCenter
        open={open}
        onClose={handleClose}
        onUnreadCountChange={handleUnreadCountChange}
      />
    </>
  );
};

export default NotificationBell;
