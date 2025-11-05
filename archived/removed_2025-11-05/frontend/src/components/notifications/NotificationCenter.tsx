import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Drawer,
  Typography,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Badge,
  Chip,
  Button,
  CircularProgress,
  Divider,
  Alert,
  Menu,
  MenuItem,
  Tooltip,
} from '@mui/material';
import {
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  Archive as ArchiveIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  DoneAll as DoneAllIcon,
  Inventory as InventoryIcon,
  ShoppingCart as ShoppingCartIcon,
  Receipt as ReceiptIcon,
  Person as PersonIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Error as ErrorIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import notificationService from '../../services/notificationService';
import type {
  Notification,
  NotificationListResponse,
  NotificationType,
  NotificationPriority,
} from '../../types/notification';

interface NotificationCenterProps {
  open: boolean;
  onClose: () => void;
  onUnreadCountChange?: (count: number) => void;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({
  open,
  onClose,
  onUnreadCountChange,
}) => {
  const [activeTab, setActiveTab] = useState<'all' | 'unread'>('all');
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [page, setPage] = useState(0);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);

  // Load notifications
  const loadNotifications = useCallback(async (refresh = false) => {
    try {
      setLoading(true);
      const skip = refresh ? 0 : page * 50;
      const response: NotificationListResponse = await notificationService.getNotifications({
        skip,
        limit: 50,
        unread_only: activeTab === 'unread',
      });

      if (refresh) {
        setNotifications(response.notifications);
        setPage(0);
      } else {
        setNotifications((prev) => [...prev, ...response.notifications]);
      }

      setUnreadCount(response.unread_count);
      setTotal(response.total);
      setHasMore(response.has_more);

      if (onUnreadCountChange) {
        onUnreadCountChange(response.unread_count);
      }
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  }, [page, activeTab, onUnreadCountChange]);

  useEffect(() => {
    if (open) {
      loadNotifications(true);
    }
  }, [open, activeTab]);

  // Get icon based on notification type
  const getNotificationIcon = (type: NotificationType) => {
    const iconMap: Record<string, React.ReactElement> = {
      low_stock: <InventoryIcon />,
      out_of_stock: <ErrorIcon />,
      new_order: <ShoppingCartIcon />,
      invoice_created: <ReceiptIcon />,
      leave_request: <PersonIcon />,
      system_alert: <WarningIcon />,
    };
    return iconMap[type] || <NotificationsIcon />;
  };

  // Get color based on priority
  const getPriorityColor = (priority: NotificationPriority): 'default' | 'info' | 'warning' | 'error' => {
    const colorMap: Record<NotificationPriority, 'default' | 'info' | 'warning' | 'error'> = {
      low: 'default',
      medium: 'info',
      high: 'warning',
      critical: 'error',
    };
    return colorMap[priority];
  };

  // Mark notification as read
  const handleMarkAsRead = async (notification: Notification) => {
    if (notification.is_read) return;

    try {
      await notificationService.markAsRead(notification.id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === notification.id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
      if (onUnreadCountChange) {
        onUnreadCountChange(Math.max(0, unreadCount - 1));
      }
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  // Mark all as read
  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
      if (onUnreadCountChange) {
        onUnreadCountChange(0);
      }
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  // Delete notification
  const handleDelete = async (notification: Notification) => {
    try {
      await notificationService.deleteNotification(notification.id);
      setNotifications((prev) => prev.filter((n) => n.id !== notification.id));
      if (!notification.is_read) {
        setUnreadCount((prev) => Math.max(0, prev - 1));
        if (onUnreadCountChange) {
          onUnreadCountChange(Math.max(0, unreadCount - 1));
        }
      }
      setTotal((prev) => prev - 1);
      handleCloseMenu();
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  // Archive notification
  const handleArchive = async (notification: Notification) => {
    try {
      await notificationService.archiveNotification(notification.id);
      setNotifications((prev) => prev.filter((n) => n.id !== notification.id));
      if (!notification.is_read) {
        setUnreadCount((prev) => Math.max(0, prev - 1));
        if (onUnreadCountChange) {
          onUnreadCountChange(Math.max(0, unreadCount - 1));
        }
      }
      handleCloseMenu();
    } catch (error) {
      console.error('Failed to archive notification:', error);
    }
  };

  // Handle notification click
  const handleNotificationClick = (notification: Notification) => {
    handleMarkAsRead(notification);
    if (notification.action_url) {
      window.location.href = notification.action_url;
    }
  };

  // Menu handlers
  const handleOpenMenu = (event: React.MouseEvent<HTMLElement>, notification: Notification) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedNotification(notification);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
    setSelectedNotification(null);
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: { width: { xs: '100%', sm: 400 } },
      }}
    >
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: 1,
            borderColor: 'divider',
          }}
        >
          <Typography variant="h6">Notifications</Typography>
          <Box>
            {unreadCount > 0 && (
              <Tooltip title="Mark all as read">
                <IconButton size="small" onClick={handleMarkAllAsRead} sx={{ mr: 1 }}>
                  <DoneAllIcon />
                </IconButton>
              </Tooltip>
            )}
            <Tooltip title="Refresh">
              <IconButton size="small" onClick={() => loadNotifications(true)} sx={{ mr: 1 }}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <IconButton size="small" onClick={onClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Tabs */}
        <Tabs
          value={activeTab}
          onChange={(_, value) => setActiveTab(value)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab
            label={
              <Badge badgeContent={total} color="primary" max={99}>
                All
              </Badge>
            }
            value="all"
          />
          <Tab
            label={
              <Badge badgeContent={unreadCount} color="error" max={99}>
                Unread
              </Badge>
            }
            value="unread"
          />
        </Tabs>

        {/* Notification List */}
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {loading && notifications.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : notifications.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <NotificationsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography color="text.secondary">
                {activeTab === 'unread' ? 'No unread notifications' : 'No notifications yet'}
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {notifications.map((notification, index) => (
                <React.Fragment key={notification.id}>
                  <ListItem
                    sx={{
                      cursor: notification.action_url ? 'pointer' : 'default',
                      bgcolor: notification.is_read ? 'transparent' : 'action.hover',
                      '&:hover': { bgcolor: 'action.selected' },
                      position: 'relative',
                    }}
                    onClick={() => handleNotificationClick(notification)}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        onClick={(e) => handleOpenMenu(e, notification)}
                        size="small"
                      >
                        <MoreVertIcon />
                      </IconButton>
                    }
                  >
                    <ListItemIcon>
                      <Box
                        sx={{
                          color: `${getPriorityColor(notification.priority)}.main`,
                          display: 'flex',
                          alignItems: 'center',
                        }}
                      >
                        {getNotificationIcon(notification.type)}
                      </Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Typography
                            variant="subtitle2"
                            sx={{ fontWeight: notification.is_read ? 'normal' : 'bold' }}
                          >
                            {notification.title}
                          </Typography>
                          {!notification.is_read && (
                            <Box
                              sx={{
                                width: 8,
                                height: 8,
                                borderRadius: '50%',
                                bgcolor: 'primary.main',
                              }}
                            />
                          )}
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                            {notification.message}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip
                              label={notification.priority}
                              size="small"
                              color={getPriorityColor(notification.priority)}
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                            <Typography variant="caption" color="text.secondary">
                              {formatDistanceToNow(new Date(notification.created_at), {
                                addSuffix: true,
                              })}
                            </Typography>
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < notifications.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}

          {/* Load More */}
          {hasMore && (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Button
                onClick={() => {
                  setPage((p) => p + 1);
                  loadNotifications(false);
                }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={20} /> : 'Load More'}
              </Button>
            </Box>
          )}
        </Box>
      </Box>

      {/* Context Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleCloseMenu}>
        {selectedNotification && !selectedNotification.is_read && (
          <MenuItem
            onClick={() => {
              if (selectedNotification) handleMarkAsRead(selectedNotification);
              handleCloseMenu();
            }}
          >
            <ListItemIcon>
              <CheckCircleIcon fontSize="small" />
            </ListItemIcon>
            Mark as read
          </MenuItem>
        )}
        <MenuItem
          onClick={() => {
            if (selectedNotification) handleArchive(selectedNotification);
          }}
        >
          <ListItemIcon>
            <ArchiveIcon fontSize="small" />
          </ListItemIcon>
          Archive
        </MenuItem>
        <MenuItem
          onClick={() => {
            if (selectedNotification) handleDelete(selectedNotification);
          }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <Typography color="error">Delete</Typography>
        </MenuItem>
      </Menu>
    </Drawer>
  );
};

export default NotificationCenter;
