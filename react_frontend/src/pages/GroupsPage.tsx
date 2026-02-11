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
  Button,
  TextInput,
  Textarea
} from '@tremor/react';

interface Group {
  id?: number;
  name: string;
  description: string;
}

const GroupsPage: React.FC = () => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingGroup, setEditingGroup] = useState<Group | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const groupsData = await apiService.getGroups();
      setGroups(groupsData);
    } catch (error) {
      console.error('Error loading groups:', error);
      alert('Error al cargar grupos');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: ''
    });
    setEditingGroup(null);
    setShowForm(false);
  };

  const handleCreateGroup = () => {
    resetForm();
    setShowForm(true);
  };

  const handleEditGroup = (group: Group) => {
    setFormData({
      name: group.name,
      description: group.description || ''
    });
    setEditingGroup(group);
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const groupData = {
        name: formData.name,
        description: formData.description
      };

      if (editingGroup) {
        await apiService.updateGroup(editingGroup.id!, groupData);
        alert('Grupo actualizado exitosamente');
      } else {
        await apiService.createGroup(groupData);
        alert('Grupo creado exitosamente');
      }

      resetForm();
      loadGroups();
    } catch (error) {
      console.error('Error saving group:', error);
      alert('Error al guardar grupo');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteGroup = async (groupId: number) => {
    if (!confirm('¿Está seguro de que desea eliminar este grupo?')) return;

    try {
      await apiService.deleteGroup(groupId);
      alert('Grupo eliminado exitosamente');
      loadGroups();
    } catch (error) {
      console.error('Error deleting group:', error);
      alert('Error al eliminar grupo');
    }
  };

  return (
    <div className="p-6 sm:p-10">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-4 sm:mb-0">Gestión de Grupos</h1>
        <Button onClick={handleCreateGroup}>Crear Nuevo Grupo</Button>
      </div>

      {/* Group Form Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <Card className="max-w-2xl w-full">
            <form onSubmit={handleSubmit} className="space-y-6">
              <h2 className="text-xl font-semibold">{editingGroup ? 'Editar Grupo' : 'Crear Nuevo Grupo'}</h2>
              
              <div>
                <label className="text-sm font-medium text-slate-600">Nombre del Grupo *</label>
                <TextInput value={formData.name} onValueChange={(value) => setFormData(prev => ({ ...prev, name: value }))} required placeholder="Ej: Equipo de Respuesta Azul" />
              </div>

              <div>
                <label className="text-sm font-medium text-slate-600">Descripción</label>
                <Textarea value={formData.description} onValueChange={(value) => setFormData(prev => ({ ...prev, description: value }))} rows={4} placeholder="Describa el propósito y alcance del grupo..." />
              </div>

              <div className="flex justify-end space-x-2 pt-4 border-t border-slate-200">
                <Button type="button" variant="secondary" onClick={resetForm}>Cancelar</Button>
                <Button type="submit" loading={loading} disabled={loading}>{editingGroup ? 'Guardar Cambios' : 'Crear Grupo'}</Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* Groups Table */}
      <Card>
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>Nombre</TableHeaderCell>
              <TableHeaderCell>Descripción</TableHeaderCell>
              <TableHeaderCell>Acciones</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {groups.map((group) => (
              <TableRow key={group.id} className="hover:bg-slate-50">
                <TableCell>
                  <p className="font-medium text-slate-900">{group.name}</p>
                </TableCell>
                <TableCell>
                  <p className="text-sm text-slate-600 max-w-xs truncate">{group.description || 'Sin descripción'}</p>
                </TableCell>
                <TableCell className="space-x-2">
                  <Button size="xs" variant="secondary" onClick={() => handleEditGroup(group)}>Editar</Button>
                  <Button size="xs" variant="secondary" color="red" onClick={() => handleDeleteGroup(group.id!)}>Eliminar</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {groups.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-500">No hay grupos registrados aún.</p>
            <Button onClick={handleCreateGroup} className="mt-4">Crear el primer grupo</Button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default GroupsPage;