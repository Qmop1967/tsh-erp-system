'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/dashboard-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Megaphone,
  Plus,
  Edit,
  Trash2,
  Send,
  Calendar,
  Users,
  AlertTriangle,
  CheckCircle2,
  Clock,
  MoreVertical,
  Eye,
  EyeOff,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow, format } from 'date-fns';

interface Announcement {
  id: string;
  title: string;
  content: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  status: 'draft' | 'scheduled' | 'published' | 'expired' | 'archived';
  target_type: 'all' | 'roles' | 'branches' | 'users';
  target_roles?: string[];
  target_branches?: number[];
  requires_acknowledgment: boolean;
  publish_at?: string;
  expires_at?: string;
  delivery_channels: string[];
  created_at: string;
  updated_at: string;
  created_by: number;
}

const SEVERITY_CONFIG = {
  info: { label: 'Info', color: 'bg-blue-100 text-blue-800', icon: '💡' },
  warning: { label: 'Warning', color: 'bg-amber-100 text-amber-800', icon: '⚠️' },
  error: { label: 'Error', color: 'bg-red-100 text-red-800', icon: '❌' },
  critical: { label: 'Critical', color: 'bg-purple-100 text-purple-800', icon: '🚨' },
};

const STATUS_CONFIG = {
  draft: { label: 'Draft', color: 'bg-gray-100 text-gray-800' },
  scheduled: { label: 'Scheduled', color: 'bg-blue-100 text-blue-800' },
  published: { label: 'Published', color: 'bg-green-100 text-green-800' },
  expired: { label: 'Expired', color: 'bg-orange-100 text-orange-800' },
  archived: { label: 'Archived', color: 'bg-gray-100 text-gray-600' },
};

export default function AnnouncementsPage() {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedAnnouncement, setSelectedAnnouncement] = useState<Announcement | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    severity: 'info' as const,
    target_type: 'all' as const,
    target_roles: [] as string[],
    requires_acknowledgment: false,
    publish_at: '',
    expires_at: '',
    delivery_channels: ['in_app'] as string[],
  });

  const handleCreate = async () => {
    setIsLoading(true);
    try {
      // TODO: API call to create announcement
      // const response = await fetch('/api/neurolink/announcements', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(formData)
      // });
      // const newAnnouncement = await response.json();
      // setAnnouncements([...announcements, newAnnouncement]);

      setIsCreateOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to create announcement:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = async () => {
    if (!selectedAnnouncement) return;

    setIsLoading(true);
    try {
      // TODO: API call to update announcement
      // const response = await fetch(`/api/neurolink/announcements/${selectedAnnouncement.id}`, {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(formData)
      // });

      setIsEditOpen(false);
      setSelectedAnnouncement(null);
      resetForm();
    } catch (error) {
      console.error('Failed to update announcement:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this announcement?')) return;

    try {
      // TODO: API call to delete announcement
      // await fetch(`/api/neurolink/announcements/${id}`, { method: 'DELETE' });
      setAnnouncements(announcements.filter(a => a.id !== id));
    } catch (error) {
      console.error('Failed to delete announcement:', error);
    }
  };

  const handlePublish = async (id: string) => {
    try {
      // TODO: API call to publish announcement
      // await fetch(`/api/neurolink/announcements/${id}/publish`, { method: 'POST' });
    } catch (error) {
      console.error('Failed to publish announcement:', error);
    }
  };

  const openEditDialog = (announcement: Announcement) => {
    setSelectedAnnouncement(announcement);
    setFormData({
      title: announcement.title,
      content: announcement.content,
      severity: announcement.severity,
      target_type: announcement.target_type,
      target_roles: announcement.target_roles || [],
      requires_acknowledgment: announcement.requires_acknowledgment,
      publish_at: announcement.publish_at || '',
      expires_at: announcement.expires_at || '',
      delivery_channels: announcement.delivery_channels,
    });
    setIsEditOpen(true);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      severity: 'info',
      target_type: 'all',
      target_roles: [],
      requires_acknowledgment: false,
      publish_at: '',
      expires_at: '',
      delivery_channels: ['in_app'],
    });
  };

  const filteredAnnouncements = filter === 'all'
    ? announcements
    : announcements.filter(a => a.status === filter);

  return (
    <DashboardLayout>
      <div className="p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Megaphone className="h-8 w-8 text-blue-600" />
              Announcements
            </h1>
            <p className="text-gray-500 mt-1">
              Manage system-wide announcements and notifications
            </p>
          </div>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Create Announcement
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-6 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{announcements.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Published</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {announcements.filter(a => a.status === 'published').length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Drafts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-600">
                {announcements.filter(a => a.status === 'draft').length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Scheduled</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {announcements.filter(a => a.status === 'scheduled').length}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          {['all', 'draft', 'scheduled', 'published', 'expired'].map((status) => (
            <Button
              key={status}
              variant={filter === status ? 'default' : 'outline'}
              onClick={() => setFilter(status)}
              size="sm"
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </Button>
          ))}
        </div>

        {/* Announcements List */}
        <Card>
          <CardHeader>
            <CardTitle>All Announcements</CardTitle>
            <CardDescription>
              {filteredAnnouncements.length} announcement{filteredAnnouncements.length !== 1 ? 's' : ''}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {filteredAnnouncements.length === 0 ? (
              <div className="text-center py-12">
                <Megaphone className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No announcements</h3>
                <p className="text-gray-500 mb-4">Get started by creating your first announcement</p>
                <Button onClick={() => setIsCreateOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Announcement
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredAnnouncements.map((announcement) => {
                  const severity = SEVERITY_CONFIG[announcement.severity];
                  const status = STATUS_CONFIG[announcement.status];

                  return (
                    <div
                      key={announcement.id}
                      className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          {/* Title and Badges */}
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xl">{severity.icon}</span>
                            <h3 className="font-semibold text-lg">{announcement.title}</h3>
                            <Badge className={cn('text-xs', severity.color)}>
                              {severity.label}
                            </Badge>
                            <Badge className={cn('text-xs', status.color)}>
                              {status.label}
                            </Badge>
                          </div>

                          {/* Content Preview */}
                          <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                            {announcement.content}
                          </p>

                          {/* Metadata */}
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <div className="flex items-center gap-1">
                              <Users className="h-3 w-3" />
                              <span>
                                {announcement.target_type === 'all'
                                  ? 'All users'
                                  : announcement.target_type === 'roles'
                                  ? `Roles: ${announcement.target_roles?.join(', ')}`
                                  : announcement.target_type
                                }
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Send className="h-3 w-3" />
                              <span>{announcement.delivery_channels.join(', ')}</span>
                            </div>
                            {announcement.publish_at && (
                              <div className="flex items-center gap-1">
                                <Calendar className="h-3 w-3" />
                                <span>
                                  {announcement.status === 'scheduled'
                                    ? `Scheduled: ${format(new Date(announcement.publish_at), 'MMM d, yyyy')}`
                                    : `Published: ${formatDistanceToNow(new Date(announcement.publish_at), { addSuffix: true })}`
                                  }
                                </span>
                              </div>
                            )}
                            {announcement.requires_acknowledgment && (
                              <div className="flex items-center gap-1">
                                <CheckCircle2 className="h-3 w-3" />
                                <span>Requires ACK</span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2 ml-4">
                          {announcement.status === 'draft' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handlePublish(announcement.id)}
                            >
                              <Send className="h-4 w-4 mr-1" />
                              Publish
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => openEditDialog(announcement)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDelete(announcement.id)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Create/Edit Dialog */}
        <Dialog open={isCreateOpen || isEditOpen} onOpenChange={(open) => {
          if (!open) {
            setIsCreateOpen(false);
            setIsEditOpen(false);
            setSelectedAnnouncement(null);
            resetForm();
          }
        }}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {isEditOpen ? 'Edit Announcement' : 'Create Announcement'}
              </DialogTitle>
              <DialogDescription>
                {isEditOpen
                  ? 'Update the announcement details below'
                  : 'Create a new announcement to notify users across the system'
                }
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              {/* Title */}
              <div className="space-y-2">
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g., System Maintenance Scheduled"
                />
              </div>

              {/* Content */}
              <div className="space-y-2">
                <Label htmlFor="content">Message *</Label>
                <Textarea
                  id="content"
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  placeholder="Enter the announcement message..."
                  rows={5}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Severity */}
                <div className="space-y-2">
                  <Label htmlFor="severity">Severity</Label>
                  <Select
                    value={formData.severity}
                    onValueChange={(value: any) => setFormData({ ...formData, severity: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="info">💡 Info</SelectItem>
                      <SelectItem value="warning">⚠️ Warning</SelectItem>
                      <SelectItem value="error">❌ Error</SelectItem>
                      <SelectItem value="critical">🚨 Critical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Target Type */}
                <div className="space-y-2">
                  <Label htmlFor="target_type">Target Audience</Label>
                  <Select
                    value={formData.target_type}
                    onValueChange={(value: any) => setFormData({ ...formData, target_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Users</SelectItem>
                      <SelectItem value="roles">Specific Roles</SelectItem>
                      <SelectItem value="branches">Specific Branches</SelectItem>
                      <SelectItem value="users">Specific Users</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Target Roles (conditional) */}
              {formData.target_type === 'roles' && (
                <div className="space-y-2">
                  <Label htmlFor="target_roles">Target Roles (comma-separated)</Label>
                  <Input
                    id="target_roles"
                    value={formData.target_roles.join(', ')}
                    onChange={(e) => setFormData({
                      ...formData,
                      target_roles: e.target.value.split(',').map(r => r.trim())
                    })}
                    placeholder="e.g., sales_rep, warehouse_manager"
                  />
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                {/* Publish At */}
                <div className="space-y-2">
                  <Label htmlFor="publish_at">Publish Date (optional)</Label>
                  <Input
                    id="publish_at"
                    type="datetime-local"
                    value={formData.publish_at}
                    onChange={(e) => setFormData({ ...formData, publish_at: e.target.value })}
                  />
                </div>

                {/* Expires At */}
                <div className="space-y-2">
                  <Label htmlFor="expires_at">Expiry Date (optional)</Label>
                  <Input
                    id="expires_at"
                    type="datetime-local"
                    value={formData.expires_at}
                    onChange={(e) => setFormData({ ...formData, expires_at: e.target.value })}
                  />
                </div>
              </div>

              {/* Delivery Channels */}
              <div className="space-y-2">
                <Label>Delivery Channels</Label>
                <div className="flex gap-4">
                  {['in_app', 'email', 'push', 'sms'].map((channel) => (
                    <label key={channel} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.delivery_channels.includes(channel)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({
                              ...formData,
                              delivery_channels: [...formData.delivery_channels, channel]
                            });
                          } else {
                            setFormData({
                              ...formData,
                              delivery_channels: formData.delivery_channels.filter(c => c !== channel)
                            });
                          }
                        }}
                        className="rounded"
                      />
                      <span className="text-sm capitalize">{channel.replace('_', ' ')}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Requires Acknowledgment */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="requires_ack"
                  checked={formData.requires_acknowledgment}
                  onChange={(e) => setFormData({
                    ...formData,
                    requires_acknowledgment: e.target.checked
                  })}
                  className="rounded"
                />
                <Label htmlFor="requires_ack" className="cursor-pointer">
                  Require user acknowledgment
                </Label>
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setIsCreateOpen(false);
                  setIsEditOpen(false);
                  setSelectedAnnouncement(null);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={isEditOpen ? handleUpdate : handleCreate}
                disabled={!formData.title || !formData.content || isLoading}
              >
                {isLoading ? 'Saving...' : isEditOpen ? 'Update' : 'Create'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
