import React, { useState, useEffect } from 'react';
import { apiService } from '../services/apiService';
import {
  Card,
  Table,
  TableHead,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  Badge,
  Button,
  TextInput,
  Select,
  SelectItem
} from '@tremor/react';
import type { User, Group } from '../types/user';
import UserCrossReferenceModal from '../components/admin/UserCrossReferenceModal';

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    position: '',
    city: '',
    role: '',
    password: '',
    group_id: ''
  });
  const [loading, setLoading] = useState(false);
  const [exportFilters, setExportFilters] = useState({
    status: '',
    role: ''
  });
  const [showCrossReferenceModal, setShowCrossReferenceModal] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);

  useEffect(() => {
    loadUsers();
    loadGroups();
    loadCurrentUser();
  }, []);

  const loadUsers = async () => {
    try {
      const usersData = await apiService.getUsers();
      setUsers(usersData);
    } catch (error) {
      console.error('Error loading users:', error);
      alert('Error al cargar usuarios');
    }
  };

  const loadGroups = async () => {
    try {
      const groupsData = await apiService.getGroups();
      setGroups(groupsData);
    } catch (error) {
      console.error('Error loading groups:', error);
    }
  };

  const loadCurrentUser = async () => {
    try {
      const user = await apiService.getCurrentUser();
      setCurrentUser(user);
    } catch (error) {
      console.error('Error loading current user:', error);
    }
  };

  const handleExportUsers = async () => {
    try {
      const filters: { status?: 'active' | 'inactive', role?: string } = {};
      if (exportFilters.status) filters.status = exportFilters.status as 'active' | 'inactive';
      if (exportFilters.role) filters.role = exportFilters.role;
      const blob = await apiService.exportUsers(filters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'usuarios_export.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting users:', error);
      alert('Error al exportar usuarios');
    }
  };

  const resetForm = () => {
    setFormData({
      full_name: '',
      email: '',
      position: '',
      city: '',
      role: '',
      password: '',
      group_id: ''
    });
    setEditingUser(null);
    setShowForm(false);
  };

  const handleCreateUser = () => {
    resetForm();
    setShowForm(true);
  };

  const handleEditUser = (user: User) => {
    setFormData({
      full_name: user.full_name,
      email: user.email,
      position: user.position || '',
      city: user.city || '',
      role: user.role,
      password: '',
      group_id: user.group_id?.toString() || ''
    });
    setEditingUser(user);
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const userData: any = {
        email: formData.email,
        full_name: formData.full_name,
        position: formData.position,
        city: formData.city,
        role: formData.role,
      };
      if (formData.password) {
        userData.password = formData.password;
      }
      if (currentUser?.role === 'Administrador' && formData.group_id) {
        userData.group_id = parseInt(formData.group_id);
      }

      if (editingUser) {
        await apiService.updateUser(editingUser.user_id!, userData);
        alert('Usuario actualizado exitosamente');
      } else {
        await apiService.createUser(userData);
        alert('Usuario creado exitosamente');
      }

      resetForm();
      loadUsers();
    } catch (error) {
      console.error('Error saving user:', error);
      alert('Error al guardar usuario');
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivateUser = async (userId: number) => {
    const reason = prompt('Razón para desactivar (opcional):');
    if (reason === null) return; // Cancelled

    try {
      await apiService.deactivateUser(userId, reason || undefined);
      alert('Usuario desactivado exitosamente');
      loadUsers();
    } catch (error) {
      console.error('Error deactivating user:', error);
      alert('Error al desactivar usuario');
    }
  };

  const handleActivateUser = async (userId: number) => {
    if (!confirm('¿Está seguro de que desea activar este usuario?')) return;

    try {
      await apiService.activateUser(userId);
      alert('Usuario activado exitosamente');
      loadUsers();
    } catch (error) {
      console.error('Error activating user:', error);
      alert('Error al activar usuario');
    }
  };

  const isAdmin = currentUser?.role === 'Administrador';

  const roleColorMap: { [key: string]: string } = {
    'Administrador': 'emerald',
    'Líder IRT': 'orange',
    'Miembro IRT': 'sky',
    'Empleado': 'slate'
  };

  return (
    <div className="p-6 sm:p-10">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-4 sm:mb-0">Gestión de Usuarios</h1>
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
          <div className="flex space-x-2">
            <Select value={exportFilters.status} onValueChange={(value) => setExportFilters(prev => ({ ...prev, status: value }))}>
              <SelectItem value="">Todos los Estados</SelectItem>
              <SelectItem value="active">Activos</SelectItem>
              <SelectItem value="inactive">Inactivos</SelectItem>
            </Select>
            <Select value={exportFilters.role} onValueChange={(value) => setExportFilters(prev => ({ ...prev, role: value }))}>
              <SelectItem value="">Todos los Roles</SelectItem>
              <SelectItem value="Empleado">Empleado</SelectItem>
              <SelectItem value="Miembro IRT">Miembro IRT</SelectItem>
              <SelectItem value="Líder IRT">Líder IRT</SelectItem>
              <SelectItem value="Administrador">Administrador</SelectItem>
            </Select>
            <Button onClick={() => handleExportUsers()}>Exportar</Button>
          </div>
          <Button onClick={handleCreateUser}>Crear Nuevo Usuario</Button>
        </div>
      </div>

      {/* User Form Modal */}
      {showForm && (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-black bg-opacity-50">
          <Card className="max-w-2xl w-full overflow-visible relative z-40">
            <form onSubmit={handleSubmit} className="space-y-6">
              <h2 className="text-xl font-semibold">{editingUser ? 'Editar Usuario' : 'Crear Nuevo Usuario'}</h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-slate-600">Nombre Completo *</label>
                  <TextInput value={formData.full_name} onValueChange={(value) => setFormData(prev => ({ ...prev, full_name: value }))} required />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-600">Email *</label>
                  <TextInput type="email" value={formData.email} onValueChange={(value) => setFormData(prev => ({ ...prev, email: value }))} required />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-600">Cargo</label>
                  <TextInput value={formData.position} onValueChange={(value) => setFormData(prev => ({ ...prev, position: value }))} placeholder="Ej: Analista de Seguridad" />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-600">Ciudad o Sede</label>
                  <TextInput value={formData.city} onValueChange={(value) => setFormData(prev => ({ ...prev, city: value }))} placeholder="Ej: Bogotá" />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-600">Contraseña {editingUser ? '(Opcional)' : '*'}</label>
                  <TextInput type="password" value={formData.password} onValueChange={(value) => setFormData(prev => ({ ...prev, password: value }))} placeholder={editingUser ? 'Dejar en blanco para no cambiar' : 'Mínimo 8 caracteres'} required={!editingUser} />
                </div>
                <div className="relative z-50">
                  <label className="text-sm font-medium text-slate-600">Rol *</label>
                  <Select value={formData.role} onValueChange={(value) => setFormData(prev => ({ ...prev, role: value }))} required>
                    <SelectItem value="">Seleccionar rol...</SelectItem>
                    <SelectItem value="Empleado">Empleado</SelectItem>
                    <SelectItem value="Miembro IRT">Miembro IRT</SelectItem>
                    <SelectItem value="Líder IRT">Líder IRT</SelectItem>
                    <SelectItem value="Administrador">Administrador</SelectItem>
                  </Select>
                </div>
                <div className="sm:col-span-2 relative z-50">
                  <label className="text-sm font-medium text-slate-600">Grupo de Trabajo</label>
                  <Select value={formData.group_id} onValueChange={(value) => setFormData(prev => ({ ...prev, group_id: value }))} disabled={!isAdmin}>
                    <SelectItem value="">Sin Grupo Asignado</SelectItem>
                    {groups.map(group => (
                      <SelectItem key={group.id} value={String(group.id)}>
                        {group.name}
                      </SelectItem>
                    ))}
                  </Select>
                  {!isAdmin && <p className="text-xs text-slate-500 mt-1">Solo los administradores pueden cambiar el grupo.</p>}
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4 border-t border-slate-200">
                <Button type="button" variant="secondary" onClick={resetForm}>Cancelar</Button>
                <Button type="submit" loading={loading} disabled={loading}>{editingUser ? 'Guardar Cambios' : 'Crear Usuario'}</Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* Users Table */}
      <Card>
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>Nombre</TableHeaderCell>
              <TableHeaderCell>Email</TableHeaderCell>
              <TableHeaderCell>Rol</TableHeaderCell>
              <TableHeaderCell>Estado</TableHeaderCell>
              <TableHeaderCell>Grupo</TableHeaderCell>
              <TableHeaderCell>Acciones</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.user_id} className="hover:bg-slate-50">
                <TableCell>
                  <p className="font-medium text-slate-900">{user.full_name}</p>
                  {user.position && <p className="text-sm text-slate-500">{user.position}</p>}
                </TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Badge color={roleColorMap[user.role] || 'gray'}>{user.role}</Badge>
                </TableCell>
                <TableCell>
                  <Badge color={user.is_active ? 'green' : 'red'}>
                    {user.is_active ? 'Activo' : 'Inactivo'}
                  </Badge>
                </TableCell>
                <TableCell>{groups.find(g => g.id === user.group_id)?.name || 'Sin Grupo'}</TableCell>
                <TableCell className="space-x-2">
                  <Button size="xs" variant="secondary" onClick={() => handleEditUser(user)}>Editar</Button>
                  {isAdmin && <Button size="xs" variant="secondary" onClick={() => { setSelectedUserId(user.user_id!); setShowCrossReferenceModal(true); }}>Referencias</Button>}
                  {isAdmin && user.user_id !== currentUser?.user_id && (
                    user.is_active ? (
                      <Button size="xs" variant="secondary" color="orange" onClick={() => handleDeactivateUser(user.user_id!)}>Desactivar</Button>
                    ) : (
                      <Button size="xs" variant="secondary" color="green" onClick={() => handleActivateUser(user.user_id!)}>Activar</Button>
                    )
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {users.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-500">No hay usuarios registrados aún.</p>
            <Button onClick={handleCreateUser} className="mt-4">Crear el primer usuario</Button>
          </div>
        )}
      </Card>

      {/* Cross Reference Modal */}
      {showCrossReferenceModal && selectedUserId && (
        <UserCrossReferenceModal
          userId={selectedUserId}
          onClose={() => { setShowCrossReferenceModal(false); setSelectedUserId(null); }}
        />
      )}
    </div>
  );
};

export default UsersPage;