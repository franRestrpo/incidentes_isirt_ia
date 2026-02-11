// src/pages/AuditDashboard.tsx
import { useState, useEffect } from 'react';
import { Title, Grid, Col, SearchSelect, SearchSelectItem } from '@tremor/react';
import { apiService } from '../services/apiService'; // Use the centralized apiService

import MetricsCards from '../components/audit/MetricsCards';
import UserActivityGraph from '../components/audit/UserActivityGraph';

// Define interfaces for our data structures for type safety
interface User {
  user_id: number;
  full_name: string;
}

interface UserForSelect {
  id: number;
  name: string;
}

export default function AuditDashboard() {
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [users, setUsers] = useState<UserForSelect[]>([]);
  const [activityData, setActivityData] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Effect to load the list of users for the dropdown
  useEffect(() => {
    const loadUsers = async () => {
      try {
        const userList: User[] = await apiService.getUsers(); // Use apiService
        // Adapt the user list to the format expected by the SearchSelect component
        const formattedUsers = userList.map(user => ({ id: user.user_id, name: user.full_name }));
        setUsers(formattedUsers);
      } catch (err: any) {
        setError('No se pudo cargar la lista de usuarios.');
      }
    };
    loadUsers();
  }, []);

  // Effect to load the activity data when a user is selected
  useEffect(() => {
    if (!selectedUserId) {
      setActivityData(null);
      return;
    }

    const loadActivity = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await apiService.getUserCrossReference(parseInt(selectedUserId, 10)); // Use apiService
        setActivityData(data);
      } catch (err: any) {
        setError(err.message);
        setActivityData(null); // Clear previous data on error
      } finally {
        setIsLoading(false);
      }
    };

    loadActivity();
  }, [selectedUserId]);

  return (
    <main className="p-6 sm:p-10">
      <Title>Auditoría de Actividad de Usuario</Title>
      <Grid numItemsLg={1} className="mt-6 gap-6">
        <Col>
          <SearchSelect 
            placeholder="Selecciona un usuario para auditar..."
            onValueChange={setSelectedUserId}
            disabled={users.length === 0}
          >
            {users.map((user) => (
              <SearchSelectItem key={user.id} value={user.id.toString()}>
                {user.name}
              </SearchSelectItem>
            ))}
          </SearchSelect>
        </Col>

        {isLoading && <p className="text-center mt-4">Cargando datos de actividad...</p>}
        {error && <p className="text-red-500 text-center mt-4">Error: {error}</p>}

        {activityData && !isLoading && (
          <div className="mt-6">
            <MetricsCards metrics={activityData.metrics} />
            <div className="mt-6 w-full h-[75vh] bg-white rounded-lg shadow-lg border border-gray-200">
              <UserActivityGraph data={activityData} />
            </div>
          </div>
        )}
      </Grid>
    </main>
  );
}
