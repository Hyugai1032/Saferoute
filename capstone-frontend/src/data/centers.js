export const centers = [
  {
    id: 1,
    name: 'Calapan Central School',
    municipality: 'Calapan City',
    lat: 13.411,
    lon: 121.18,
    capacity: 120,
    occupants: 50,
    supplies: {
      food: 85,
      water: 90,
      medicine: 70,
      blankets: 95
    },
    status: 'normal',
    contact: '09123456789',
    lastUpdate: '2024-01-15 14:30'
  },
  {
    id: 2,
    name: 'Naujan Evacuation Hall',
    municipality: 'Naujan',
    lat: 13.325,
    lon: 121.31,
    capacity: 100,
    occupants: 95,
    supplies: {
      food: 30,
      water: 25,
      medicine: 40,
      blankets: 60
    },
    status: 'critical',
    contact: '09123456790',
    lastUpdate: '2024-01-15 13:45'
  },
  {
    id: 3,
    name: 'Baco Barangay Center',
    municipality: 'Baco',
    lat: 13.346,
    lon: 121.13,
    capacity: 80,
    occupants: 80,
    supplies: {
      food: 50,
      water: 45,
      medicine: 60,
      blankets: 70
    },
    status: 'warning',
    contact: '09123456791',
    lastUpdate: '2024-01-15 15:20'
  },
  {
    id: 4,
    name: 'Puerto Galera Gymnasium',
    municipality: 'Puerto Galera',
    lat: 13.502,
    lon: 120.954,
    capacity: 150,
    occupants: 45,
    supplies: {
      food: 95,
      water: 90,
      medicine: 85,
      blankets: 80
    },
    status: 'normal',
    contact: '09123456792',
    lastUpdate: '2024-01-15 12:15'
  },
  {
    id: 5,
    name: 'Roxas Memorial Center',
    municipality: 'Roxas',
    lat: 12.589,
    lon: 121.522,
    capacity: 90,
    occupants: 88,
    supplies: {
      food: 35,
      water: 40,
      medicine: 25,
      blankets: 50
    },
    status: 'critical',
    contact: '09123456793',
    lastUpdate: '2024-01-15 16:00'
  }
]

export const getStatusColor = (center) => {
  const percentage = (center.occupants / center.capacity) * 100
  if (percentage >= 90) return '#ef4444' // Critical - Red
  if (percentage >= 70) return '#f59e0b' // Warning - Orange
  return '#10b981' // Normal - Green
}

export const getStatusText = (center) => {
  const percentage = (center.occupants / center.capacity) * 100
  if (percentage >= 90) return 'Critical'
  if (percentage >= 70) return 'Nearly Full'
  return 'Available'
}

export const getStatusLevel = (center) => {
  const percentage = (center.occupants / center.capacity) * 100
  if (percentage >= 90) return 'critical'
  if (percentage >= 70) return 'warning'
  return 'normal'
}