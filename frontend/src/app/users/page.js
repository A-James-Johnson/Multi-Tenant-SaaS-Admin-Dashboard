'use client';

import { useEffect, useState } from 'react';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import DataTable, { Modal } from '@/components/ui/DataTable';
import { usersAPI } from '@/lib/api';
import { StatusBadge, formatDateTime } from '@/lib/utils';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [pagination, setPagination] = useState({});
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [form, setForm] = useState({ email: '', first_name: '', last_name: '', phone: '', password: '', role_id: '', status: 'active' });
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  const fetchUsers = () => {
    setLoading(true);
    usersAPI.list({ page, search }).then((res) => {
      setUsers(res.data.data.results || []);
      setPagination(res.data.data);
    }).finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchUsers();
    usersAPI.roles().then((res) => setRoles(res.data.data || []));
  }, [page, search]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (editUser) {
      const { password, ...data } = form;
      await usersAPI.update(editUser.id, data);
    } else {
      await usersAPI.create(form);
    }
    setModalOpen(false);
    fetchUsers();
  };

  const columns = [
    { key: 'full_name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Phone' },
    { key: 'role', label: 'Role', render: (r) => r.role?.display_name },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
    { key: 'last_login', label: 'Last Login', render: (r) => formatDateTime(r.last_login) },
  ];

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Users</h1>
              <p className="text-muted-foreground">Manage platform users</p>
            </div>
            <button onClick={() => { setEditUser(null); setForm({ email: '', first_name: '', last_name: '', phone: '', password: '', role_id: roles[0]?.id || '', status: 'active' }); setModalOpen(true); }} className="btn-primary gap-2">
              <Plus className="h-4 w-4" /> Add User
            </button>
          </div>
          <input type="search" placeholder="Search users..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className="input max-w-sm" />
          <DataTable
            columns={columns} data={users} loading={loading} pagination={pagination} onPageChange={setPage}
            actions={(row) => (
              <div className="flex justify-end gap-1">
                <button onClick={() => { setEditUser(row); setForm({ email: row.email, first_name: row.first_name, last_name: row.last_name, phone: row.phone || '', role_id: row.role?.id, status: row.status, password: '' }); setModalOpen(true); }} className="rounded p-1.5 hover:bg-accent"><Pencil className="h-4 w-4" /></button>
                <button onClick={() => usersAPI.delete(row.id).then(fetchUsers)} className="rounded p-1.5 hover:bg-accent text-destructive"><Trash2 className="h-4 w-4" /></button>
              </div>
            )}
          />
        </div>
        <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editUser ? 'Edit User' : 'Create User'}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} className="input" placeholder="First name" required />
            <input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} className="input" placeholder="Last name" required />
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="input" placeholder="Email" required disabled={!!editUser} />
            <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="input" placeholder="Phone" />
            {!editUser && <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="input" placeholder="Password" required minLength={8} />}
            <select value={form.role_id} onChange={(e) => setForm({ ...form, role_id: Number(e.target.value) })} className="input">
              {roles.map((r) => <option key={r.id} value={r.id}>{r.display_name}</option>)}
            </select>
            <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} className="input">
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="suspended">Suspended</option>
            </select>
            <button type="submit" className="btn-primary w-full">{editUser ? 'Update' : 'Create'}</button>
          </form>
        </Modal>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
